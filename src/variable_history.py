#!/usr/bin/env python3
"""Variable History Management for NLM System

Provides logging and tracking of variable changes for multi-agent research.
"""

import sqlite3
import json
import csv
from datetime import datetime
from pathlib import Path

class VariableHistoryManager:
    """Manages history logging for variable changes"""
    
    def __init__(self, db_path="variables.db", enabled=False):
        """Initialize history manager
        
        Args:
            db_path: Path to SQLite database file
            enabled: Whether logging is enabled (default: False)
        """
        self.db_path = db_path
        self.enabled = enabled
        self._init_history_table()
    
    def _init_history_table(self):
        """Initialize the variable_history table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS variable_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                namespace TEXT NOT NULL,
                variable_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_namespace 
            ON variable_history(namespace)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_timestamp 
            ON variable_history(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def log_change(self, namespace, variable_name, old_value, new_value):
        """Log a variable change
        
        Args:
            namespace: Namespace of the variable (e.g., "agent1", "global")
            variable_name: Name of the variable
            old_value: Previous value (None if new variable)
            new_value: New value (None if variable deleted)
        """
        # Skip logging if disabled
        if not self.enabled:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO variable_history 
            (timestamp, namespace, variable_name, old_value, new_value)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, namespace, variable_name, old_value, new_value))
        
        conn.commit()
        conn.close()
    
    def enable_logging(self):
        """Enable history logging"""
        self.enabled = True
        print("📝 History logging enabled")
    
    def disable_logging(self):
        """Disable history logging"""
        self.enabled = False
        print("🚫 History logging disabled")
    
    def is_logging_enabled(self):
        """Check if logging is enabled
        
        Returns:
            bool: True if logging is enabled
        """
        return self.enabled
    
    def reset_logging(self):
        """Clear all history records
        
        Returns:
            int: Number of records cleared
        """
        count = self.clear_history()
        print(f"🗑️ Cleared {count} history records")
        return count
    
    def get_history(self, namespace=None, variable_name=None, since=None, limit=100):
        """Get variable change history
        
        Args:
            namespace: Filter by namespace (None for all)
            variable_name: Filter by variable name (None for all)
            since: ISO timestamp to filter from (None for all time)
            limit: Maximum number of records to return
            
        Returns:
            List of dictionaries with history records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM variable_history WHERE 1=1"
        params = []
        
        if namespace:
            query += " AND namespace = ?"
            params.append(namespace)
        
        if variable_name:
            query += " AND variable_name = ?"
            params.append(variable_name)
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = ['id', 'timestamp', 'namespace', 'variable_name', 'old_value', 'new_value']
        return [dict(zip(columns, row)) for row in rows]
    
    def get_namespaces(self):
        """Get list of all namespaces in history
        
        Returns:
            List of namespace strings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT namespace FROM variable_history ORDER BY namespace")
        namespaces = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return namespaces
    
    def get_variable_names(self, namespace=None):
        """Get list of variable names
        
        Args:
            namespace: Filter by namespace (None for all)
            
        Returns:
            List of variable name strings
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if namespace:
            cursor.execute("""
                SELECT DISTINCT variable_name FROM variable_history 
                WHERE namespace = ? ORDER BY variable_name
            """, (namespace,))
        else:
            cursor.execute("""
                SELECT DISTINCT variable_name FROM variable_history 
                ORDER BY variable_name
            """)
        
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return names
    
    def clear_history(self, namespace=None):
        """Clear variable history
        
        Args:
            namespace: Clear only this namespace (None for all)
            
        Returns:
            Number of records cleared
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if namespace:
            cursor.execute("DELETE FROM variable_history WHERE namespace = ?", (namespace,))
        else:
            cursor.execute("DELETE FROM variable_history")
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def export_to_file(self, filepath, format="json", namespace=None, since=None):
        """Export history to file
        
        Args:
            filepath: Output file path
            format: "json" or "csv"
            namespace: Filter by namespace (None for all)
            since: ISO timestamp to filter from (None for all time)
        """
        history = self.get_history(namespace=namespace, since=since, limit=10000)
        
        filepath = Path(filepath)
        
        if format.lower() == "json":
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            if history:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=history[0].keys())
                    writer.writeheader()
                    writer.writerows(history)
        
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'.")
    
    def get_stats(self):
        """Get history statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM variable_history")
        total_records = cursor.fetchone()[0]
        
        # Records by namespace
        cursor.execute("""
            SELECT namespace, COUNT(*) FROM variable_history 
            GROUP BY namespace ORDER BY COUNT(*) DESC
        """)
        by_namespace = dict(cursor.fetchall())
        
        # Date range
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM variable_history")
        date_range = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_records': total_records,
            'by_namespace': by_namespace,
            'earliest': date_range[0],
            'latest': date_range[1]
        }


# Convenience functions for easy access
_default_manager = None

def enable_logging(db_path="variables.db"):
    """Enable logging for the default history manager"""
    global _default_manager
    if _default_manager is None:
        _default_manager = VariableHistoryManager(db_path, enabled=True)
    else:
        _default_manager.enable_logging()

def disable_logging():
    """Disable logging for the default history manager"""
    global _default_manager
    if _default_manager:
        _default_manager.disable_logging()

def reset_logging():
    """Reset logging for the default history manager"""
    global _default_manager
    if _default_manager:
        return _default_manager.reset_logging()
    else:
        print("🚫 No logging manager initialized")
        return 0

def is_logging_enabled():
    """Check if logging is enabled"""
    global _default_manager
    return _default_manager.enabled if _default_manager else False