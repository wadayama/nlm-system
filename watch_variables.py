#!/usr/bin/env python3
"""Variable watcher for debugging SQLite variable management system.

This tool helps debug CLAUDE.md natural language macro execution by
monitoring variable changes in real-time.
"""

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set

from variable_db import VariableDB


class Colors:
    """ANSI color codes for terminal output."""
    
    GREEN = "\033[92m"    # New variables
    YELLOW = "\033[93m"   # Modified variables
    RED = "\033[91m"      # Deleted variables
    BLUE = "\033[94m"     # Headers
    CYAN = "\033[96m"     # Timestamps
    RESET = "\033[0m"     # Reset color
    BOLD = "\033[1m"      # Bold text


class VariableWatcher:
    """Monitor SQLite variable database for changes."""
    
    def __init__(self, db_path: str = "variables.db", use_colors: bool = True, show_full_names: bool = False):
        """Initialize the variable watcher.
        
        Parameters
        ----------
        db_path : str
            Path to the SQLite database file
        use_colors : bool
            Whether to use colored output
        show_full_names : bool
            Whether to show full namespace.variable names or just variable names
        """
        self.db_path = Path(db_path)
        self.db = VariableDB(db_path)
        self.use_colors = use_colors and sys.stdout.isatty()
        self.show_full_names = show_full_names
        self.last_variables: Dict[str, str] = {}
        self.watch_specific: Optional[str] = None
        
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def _format_variable_name(self, full_name: str) -> str:
        """Format variable name based on show_full_names setting."""
        if self.show_full_names:
            return f"{{{{{full_name}}}}}"
        else:
            # Extract just the variable name part after the namespace
            if "." in full_name:
                var_name = full_name.split(".", 1)[1]
                return f"{{{{{var_name}}}}}"
            else:
                return f"{{{{{full_name}}}}}"
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return self._colorize(f"[{timestamp}]", Colors.CYAN)
    
    def _print_header(self, title: str) -> None:
        """Print a colored header."""
        header = f"\n{self._colorize('=' * 50, Colors.BLUE)}"
        title_colored = self._colorize(f" {title} ", Colors.BOLD + Colors.BLUE)
        print(f"{header}\n{title_colored}\n{header}")

    def display_variables_table(self, variables: Dict[str, str]) -> None:
        """Display variables in a formatted table."""
        if not variables:
            print(self._colorize("No variables found.", Colors.YELLOW))
            return
        
        # Calculate column widths
        max_name_len = max(len(name) for name in variables.keys())
        max_value_len = max(len(str(value)) for value in variables.values())
        name_width = max(12, max_name_len + 2)
        value_width = max(15, min(max_value_len + 2, 50))  # Limit value width
        
        # Print header
        header = f"{'Variable Name':<{name_width}} | {'Value':<{value_width}}"
        separator = "-" * len(header)
        print(self._colorize(header, Colors.BOLD))
        print(self._colorize(separator, Colors.BLUE))
        
        # Print variables
        for name, value in variables.items():
            # Format variable name based on settings
            display_name = self._format_variable_name(name)
            
            # Truncate long values
            display_value = str(value)
            if len(display_value) > value_width - 2:
                display_value = display_value[:value_width-5] + "..."
            
            print(f"{display_name:<{name_width}} | {display_value}")

    def display_variables_json(self, variables: Dict[str, str]) -> None:
        """Display variables as JSON."""
        print(json.dumps(variables, indent=2))

    def display_variables_simple(self, variables: Dict[str, str]) -> None:
        """Display variables in simple format."""
        for name, value in variables.items():
            display_name = self._format_variable_name(name)
            print(f"{display_name}: {value}")

    def watch_once(self, format_type: str = "table") -> None:
        """Display all variables once."""
        self._print_header(f"Variables Snapshot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        variables = self.db.list_variables()
        
        # Display variables
        print(self._colorize("\n=== VARIABLES ===", Colors.BOLD + Colors.BLUE))
        if format_type == "json":
            self.display_variables_json(variables)
        elif format_type == "simple":
            self.display_variables_simple(variables)
        else:  # table
            self.display_variables_table(variables)
        
        print(f"\nTotal variables: {len(variables)}")
    
    def watch_specific_variable(self, var_name: str, interval: float = 1.0) -> None:
        """Watch a specific variable for changes."""
        self._print_header(f"Watching Variable: {{{{{var_name}}}}}")
        print(f"Update interval: {interval}s (Press Ctrl+C to stop)\n")
        
        last_value = None
        last_info = None
        
        try:
            while True:
                current_value = self.db.get_variable(var_name)
                current_info = self.db.get_variable_info(var_name)
                
                if current_value != last_value or current_info != last_info:
                    timestamp = self._get_timestamp()
                    
                    if current_info is None:
                        # Variable was deleted
                        if last_value is not None:
                            status = self._colorize("DELETED", Colors.RED)
                            print(f"{timestamp} {status}: Variable '{{{{{var_name}}}}}' no longer exists")
                            last_value = None
                            last_info = None
                    else:
                        # Variable was created or modified
                        if last_value is None:
                            status = self._colorize("CREATED", Colors.GREEN)
                            print(f"{timestamp} {status}: Variable '{{{{{var_name}}}}}' = '{current_value}'")
                        else:
                            status = self._colorize("MODIFIED", Colors.YELLOW)
                            print(f"{timestamp} {status}: Variable '{{{{{var_name}}}}}' changed")
                            print(f"  Old: '{last_value}'")
                            print(f"  New: '{current_value}'")
                        
                        if current_info:
                            print(f"  Created: {current_info['created_at']}")
                            print(f"  Updated: {current_info['updated_at']}")
                        
                        last_value = current_value
                        last_info = current_info
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n{self._colorize('Monitoring stopped.', Colors.BLUE)}")

    def watch_continuous(self, interval: float = 1.0, format_type: str = "table") -> None:
        """Watch all variables continuously for changes."""
        self._print_header("Continuous Variable Monitoring")
        print(f"Update interval: {interval}s (Press Ctrl+C to stop)\n")
        
        # Initialize tracking
        self.last_variables = self.db.list_variables()
        
        if self.last_variables:
            print(f"{self._get_timestamp()} Initial state ({len(self.last_variables)} variables):")
            
            print(self._colorize("Variables:", Colors.BOLD))
            for name, value in self.last_variables.items():  # Show all variables
                display_name = self._format_variable_name(name)
                truncated_value = value[:30] + "..." if len(value) > 30 else value
                print(f"  {display_name}: {truncated_value}")
        
        try:
            while True:
                time.sleep(interval)
                current_variables = self.db.list_variables()
                
                # Check for variable changes
                if current_variables != self.last_variables:
                    self._show_variable_changes(self.last_variables, current_variables)
                    self.last_variables = current_variables.copy()
                    
        except KeyboardInterrupt:
            print(f"\n\n{self._colorize('Monitoring stopped.', Colors.BLUE)}")

    def _show_variable_changes(self, old_vars: Dict[str, str], new_vars: Dict[str, str]) -> None:
        """Show changes between variable states."""
        timestamp = self._get_timestamp()
        
        # Find new variables
        for name in new_vars:
            if name not in old_vars:
                status = self._colorize("NEW", Colors.GREEN)
                display_name = self._format_variable_name(name)
                print(f"{timestamp} {status}: {display_name} = '{new_vars[name]}'")
        
        # Find modified variables
        for name in new_vars:
            if name in old_vars and old_vars[name] != new_vars[name]:
                status = self._colorize("MODIFIED", Colors.YELLOW)
                display_name = self._format_variable_name(name)
                print(f"{timestamp} {status}: {display_name} changed")
                print(f"  Old: '{old_vars[name]}'")
                print(f"  New: '{new_vars[name]}'")
        
        # Find deleted variables
        for name in old_vars:
            if name not in new_vars:
                status = self._colorize("DELETED", Colors.RED)
                display_name = self._format_variable_name(name)
                print(f"{timestamp} {status}: {display_name} removed (was '{old_vars[name]}')")

    def database_info(self) -> None:
        """Display detailed database information."""
        variables = self.db.list_variables()
        
        print(f"Database file: {self.db_path}")
        print(f"Total variables: {len(variables)}")
        
        if variables:
            # Variable name statistics
            name_lengths = [len(name) for name in variables.keys()]
            value_lengths = [len(str(value)) for value in variables.values()]
            print(f"\nVariable statistics:")
            print(f"  Name length - Shortest: {min(name_lengths)}, Longest: {max(name_lengths)}, Average: {sum(name_lengths)/len(name_lengths):.1f}")
            print(f"  Value length - Shortest: {min(value_lengths)}, Longest: {max(value_lengths)}, Average: {sum(value_lengths)/len(value_lengths):.1f}")
            
            print(f"  Variable names (first 5):")
            for name in list(variables.keys())[:5]:
                value = variables[name]
                display_value = value[:30] + "..." if len(value) > 30 else value
                print(f"    {name}: {display_value}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor SQLite variable database for changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watch_variables.py                  # Single snapshot
  python watch_variables.py -c              # Continuous monitoring  
  python watch_variables.py -c -i 0.5       # Monitor every 0.5 seconds
  python watch_variables.py --once -f json  # JSON format snapshot
  python watch_variables.py -w name         # Watch specific variable 'name'
  python watch_variables.py --info          # Database statistics
        """
    )
    
    parser.add_argument(
        "-c", "--continuous", 
        action="store_true", 
        help="Monitor continuously for changes (Ctrl+C to stop)"
    )
    
    parser.add_argument(
        "--once", 
        action="store_true", 
        help="Display variables once and exit (default behavior)"
    )
    
    parser.add_argument(
        "-i", "--interval", 
        type=float, 
        default=1.0,
        help="Update interval in seconds for continuous mode (default: 1.0)"
    )
    
    parser.add_argument(
        "-f", "--format", 
        choices=["table", "json", "simple"], 
        default="table",
        help="Output format (default: table)"
    )
    
    parser.add_argument(
        "-w", "--watch", 
        type=str,
        help="Watch a specific variable for changes"
    )
    
    parser.add_argument(
        "--no-color", 
        action="store_true", 
        help="Disable colored output"
    )
    
    parser.add_argument(
        "--db", 
        type=str, 
        default="variables.db",
        help="Database file path (default: variables.db)"
    )
    
    parser.add_argument(
        "--info", 
        action="store_true", 
        help="Show database information and statistics"
    )
    
    parser.add_argument(
        "--full-names", 
        action="store_true", 
        help="Show full namespace.variable names (default: show only variable names)"
    )
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = VariableWatcher(db_path=args.db, use_colors=not args.no_color, show_full_names=args.full_names)
    
    try:
        if args.info:
            watcher.database_info()
        elif args.watch:
            watcher.watch_specific_variable(args.watch, args.interval)
        elif args.continuous:
            watcher.watch_continuous(args.interval, args.format)
        else:
            # Default behavior: single snapshot
            watcher.watch_once(args.format)
            
    except FileNotFoundError:
        print(f"Error: Database file '{args.db}' not found.")
        print("Make sure the variable management system has been initialized.")
        sys.exit(1)
        
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()