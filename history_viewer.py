#!/usr/bin/env python3
"""History Viewer for NLM System

Command-line tool to view and analyze variable change history.
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from variable_history import VariableHistoryManager


class HistoryViewer:
    """Command-line interface for viewing variable history"""
    
    def __init__(self, db_path="variables.db"):
        """Initialize history viewer
        
        Args:
            db_path: Path to variables database
        """
        self.history_manager = VariableHistoryManager(db_path)
    
    def list_namespaces(self):
        """List all available namespaces"""
        namespaces = self.history_manager.get_namespaces()
        
        if not namespaces:
            print("No namespaces found in history")
            return
        
        print("Available namespaces:")
        for ns in namespaces:
            print(f"  {ns}")
    
    def list_variables(self, namespace=None):
        """List all variables (optionally filtered by namespace)"""
        variables = self.history_manager.get_variable_names(namespace)
        
        if not variables:
            ns_text = f" in namespace '{namespace}'" if namespace else ""
            print(f"No variables found{ns_text}")
            return
        
        ns_text = f" in namespace '{namespace}'" if namespace else ""
        print(f"Variables{ns_text}:")
        for var in variables:
            print(f"  {var}")
    
    def show_history(self, namespace=None, variable=None, limit=20, since=None):
        """Show variable change history"""
        history = self.history_manager.get_history(
            namespace=namespace,
            variable_name=variable,
            since=since,
            limit=limit
        )
        
        if not history:
            filters = []
            if namespace:
                filters.append(f"namespace='{namespace}'")
            if variable:
                filters.append(f"variable='{variable}'")
            if since:
                filters.append(f"since='{since}'")
            
            filter_text = f" ({', '.join(filters)})" if filters else ""
            print(f"No history found{filter_text}")
            return
        
        print(f"Variable history (showing {len(history)} records):")
        print("-" * 80)
        
        for record in history:
            timestamp = record['timestamp']
            namespace = record['namespace']
            variable = record['variable_name']
            old_val = record['old_value']
            new_val = record['new_value']
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp
            
            # Format change description
            if old_val is None:
                change_desc = f"Created: '{new_val}'"
            elif new_val is None:
                change_desc = f"Deleted: was '{old_val}'"
            else:
                change_desc = f"Changed: '{old_val}' → '{new_val}'"
            
            print(f"{time_str} | {namespace}.{variable}")
            print(f"  {change_desc}")
            print()
    
    def show_stats(self):
        """Show history statistics"""
        stats = self.history_manager.get_stats()
        
        print("History Statistics:")
        print(f"  Total records: {stats['total_records']}")
        
        if stats['earliest'] and stats['latest']:
            print(f"  Date range: {stats['earliest']} to {stats['latest']}")
        
        print("\n  Records by namespace:")
        for ns, count in stats['by_namespace'].items():
            print(f"    {ns}: {count}")
    
    def show_recent(self, hours=24, namespace=None):
        """Show recent changes within specified hours"""
        since_time = datetime.now() - timedelta(hours=hours)
        since_str = since_time.isoformat()
        
        print(f"Changes in the last {hours} hours:")
        self.show_history(namespace=namespace, since=since_str, limit=100)
    
    def export_history(self, filename, format="json", namespace=None, since=None):
        """Export history to file"""
        try:
            self.history_manager.export_to_file(
                filename, 
                format=format, 
                namespace=namespace, 
                since=since
            )
            print(f"History exported to {filename}")
            
            # Show file info
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"File size: {size:,} bytes")
                
        except Exception as e:
            print(f"Export failed: {e}")
    
    def search_changes(self, search_term, namespace=None, limit=50):
        """Search for changes containing specific term"""
        history = self.history_manager.get_history(
            namespace=namespace,
            limit=1000  # Get more records for searching
        )
        
        matches = []
        search_lower = search_term.lower()
        
        for record in history:
            # Search in variable name, old value, and new value
            searchable_text = " ".join([
                record['variable_name'] or "",
                record['old_value'] or "", 
                record['new_value'] or ""
            ]).lower()
            
            if search_lower in searchable_text:
                matches.append(record)
        
        if not matches:
            print(f"No changes found containing '{search_term}'")
            return
        
        print(f"Found {len(matches)} changes containing '{search_term}':")
        print("-" * 80)
        
        for record in matches[:limit]:
            timestamp = record['timestamp']
            namespace = record['namespace']
            variable = record['variable_name']
            old_val = record['old_value']
            new_val = record['new_value']
            
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp
            
            if old_val is None:
                change_desc = f"Created: '{new_val}'"
            elif new_val is None:
                change_desc = f"Deleted: was '{old_val}'"
            else:
                change_desc = f"Changed: '{old_val}' → '{new_val}'"
            
            print(f"{time_str} | {namespace}.{variable}")
            print(f"  {change_desc}")
            print()


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="NLM System History Viewer")
    parser.add_argument("--db", default="variables.db", help="Path to variables database")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List namespaces
    subparsers.add_parser("namespaces", help="List all namespaces")
    
    # List variables
    vars_parser = subparsers.add_parser("variables", help="List variables")
    vars_parser.add_argument("-n", "--namespace", help="Filter by namespace")
    
    # Show history
    history_parser = subparsers.add_parser("history", help="Show change history")
    history_parser.add_argument("-n", "--namespace", help="Filter by namespace")
    history_parser.add_argument("-v", "--variable", help="Filter by variable name")
    history_parser.add_argument("-l", "--limit", type=int, default=20, help="Limit number of records")
    history_parser.add_argument("-s", "--since", help="Show changes since timestamp (ISO format)")
    
    # Show recent changes
    recent_parser = subparsers.add_parser("recent", help="Show recent changes")
    recent_parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    recent_parser.add_argument("-n", "--namespace", help="Filter by namespace")
    
    # Show statistics
    subparsers.add_parser("stats", help="Show history statistics")
    
    # Export history
    export_parser = subparsers.add_parser("export", help="Export history to file")
    export_parser.add_argument("filename", help="Output filename")
    export_parser.add_argument("-f", "--format", choices=["json", "csv"], default="json", help="Export format")
    export_parser.add_argument("-n", "--namespace", help="Filter by namespace")
    export_parser.add_argument("-s", "--since", help="Export changes since timestamp (ISO format)")
    
    # Search changes
    search_parser = subparsers.add_parser("search", help="Search for changes")
    search_parser.add_argument("term", help="Search term")
    search_parser.add_argument("-n", "--namespace", help="Filter by namespace")
    search_parser.add_argument("-l", "--limit", type=int, default=50, help="Limit results")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize viewer
    viewer = HistoryViewer(args.db)
    
    # Execute command
    if args.command == "namespaces":
        viewer.list_namespaces()
    
    elif args.command == "variables":
        viewer.list_variables(args.namespace)
    
    elif args.command == "history":
        viewer.show_history(
            namespace=args.namespace,
            variable=args.variable,
            limit=args.limit,
            since=args.since
        )
    
    elif args.command == "recent":
        viewer.show_recent(args.hours, args.namespace)
    
    elif args.command == "stats":
        viewer.show_stats()
    
    elif args.command == "export":
        viewer.export_history(
            args.filename,
            format=args.format,
            namespace=args.namespace,
            since=args.since
        )
    
    elif args.command == "search":
        viewer.search_changes(args.term, args.namespace, args.limit)


if __name__ == "__main__":
    main()