#!/usr/bin/env python3
"""Conversation History Management for NLM System

Provides persistent storage and management of conversation history for session context.
Each session maintains its own conversation history stored in SQLite database.
"""

import sqlite3
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class ConversationHistory:
    """Manages conversation history for NLM sessions
    
    This class handles persistent storage of conversation messages including
    system prompts, user inputs, assistant responses, and tool calls.
    """
    
    def __init__(self, namespace: str, db_path: str = "variables.db"):
        """Initialize conversation history manager
        
        Args:
            namespace: Session namespace (used as conversation identifier)
            db_path: Path to SQLite database file
        """
        self.namespace = namespace
        self.db_path = Path(db_path)
        self._init_table()
    
    def _init_table(self):
        """Initialize conversation_history table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                tool_calls TEXT,
                sequence_number INTEGER NOT NULL
            )
        """)
        
        # Create indexes for efficient querying
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_namespace 
            ON conversation_history(namespace)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_sequence 
            ON conversation_history(namespace, sequence_number)
        """)
        
        conn.commit()
        conn.close()
    
    def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict]] = None):
        """Add a message to conversation history
        
        Args:
            role: Message role ('system', 'user', 'assistant', 'tool')
            content: Message content
            tool_calls: List of tool calls (for assistant messages)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get next sequence number for this namespace
        cursor.execute("""
            SELECT COALESCE(MAX(sequence_number), 0) + 1 
            FROM conversation_history 
            WHERE namespace = ?
        """, (self.namespace,))
        sequence_number = cursor.fetchone()[0]
        
        # Serialize tool_calls to JSON
        tool_calls_json = json.dumps(tool_calls) if tool_calls else None
        
        # Insert message
        cursor.execute("""
            INSERT INTO conversation_history 
            (namespace, timestamp, role, content, tool_calls, sequence_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.namespace,
            datetime.now().isoformat(),
            role,
            content,
            tool_calls_json,
            sequence_number
        ))
        
        conn.commit()
        conn.close()
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all conversation messages for this namespace
        
        Returns:
            List of message dictionaries compatible with OpenAI API format
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content, tool_calls
            FROM conversation_history
            WHERE namespace = ?
            ORDER BY sequence_number
        """, (self.namespace,))
        
        messages = []
        for row in cursor.fetchall():
            role, content, tool_calls_json = row
            
            message = {
                "role": role,
                "content": content
            }
            
            # Add tool_calls if present
            if tool_calls_json:
                try:
                    tool_calls = json.loads(tool_calls_json)
                    if tool_calls:
                        message["tool_calls"] = tool_calls
                except json.JSONDecodeError:
                    pass  # Skip invalid JSON
            
            messages.append(message)
        
        conn.close()
        return messages
    
    def get_recent_messages(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent N messages
        
        Args:
            count: Number of recent messages to retrieve
            
        Returns:
            List of recent message dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content, tool_calls
            FROM conversation_history
            WHERE namespace = ?
            ORDER BY sequence_number DESC
            LIMIT ?
        """, (self.namespace, count))
        
        messages = []
        for row in reversed(cursor.fetchall()):  # Reverse to get chronological order
            role, content, tool_calls_json = row
            
            message = {
                "role": role,
                "content": content
            }
            
            if tool_calls_json:
                try:
                    tool_calls = json.loads(tool_calls_json)
                    if tool_calls:
                        message["tool_calls"] = tool_calls
                except json.JSONDecodeError:
                    pass
            
            messages.append(message)
        
        conn.close()
        return messages
    
    def clear_all(self):
        """Clear all conversation history for this namespace"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM conversation_history
            WHERE namespace = ?
        """, (self.namespace,))
        
        conn.commit()
        conn.close()
    
    def clear_recent(self, count: int):
        """Clear the most recent N messages
        
        Args:
            count: Number of recent messages to remove
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the sequence numbers of messages to delete
        cursor.execute("""
            SELECT sequence_number
            FROM conversation_history
            WHERE namespace = ?
            ORDER BY sequence_number DESC
            LIMIT ?
        """, (self.namespace, count))
        
        sequence_numbers = [row[0] for row in cursor.fetchall()]
        
        if sequence_numbers:
            placeholders = ','.join('?' * len(sequence_numbers))
            cursor.execute(f"""
                DELETE FROM conversation_history
                WHERE namespace = ? AND sequence_number IN ({placeholders})
            """, [self.namespace] + sequence_numbers)
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics and information
        
        Returns:
            Dictionary containing conversation statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get message count by role
        cursor.execute("""
            SELECT role, COUNT(*)
            FROM conversation_history
            WHERE namespace = ?
            GROUP BY role
        """, (self.namespace,))
        
        role_counts = dict(cursor.fetchall())
        
        # Get total message count
        cursor.execute("""
            SELECT COUNT(*)
            FROM conversation_history
            WHERE namespace = ?
        """, (self.namespace,))
        
        total_messages = cursor.fetchone()[0]
        
        # Get earliest and latest timestamps
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM conversation_history
            WHERE namespace = ?
        """, (self.namespace,))
        
        timestamps = cursor.fetchone()
        earliest_time, latest_time = timestamps if timestamps[0] else (None, None)
        
        # Estimate token count (rough approximation)
        cursor.execute("""
            SELECT SUM(LENGTH(content))
            FROM conversation_history
            WHERE namespace = ? AND content IS NOT NULL
        """, (self.namespace,))
        
        total_chars = cursor.fetchone()[0] or 0
        estimated_tokens = total_chars // 4  # Rough approximation: 4 chars per token
        
        conn.close()
        
        return {
            'namespace': self.namespace,
            'total_messages': total_messages,
            'role_counts': role_counts,
            'estimated_tokens': estimated_tokens,
            'earliest_message': earliest_time,
            'latest_message': latest_time
        }
    
    def export_to_file(self, filepath: str) -> bool:
        """Export conversation history to JSON file
        
        Args:
            filepath: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, role, content, tool_calls, sequence_number
                FROM conversation_history
                WHERE namespace = ?
                ORDER BY sequence_number
            """, (self.namespace,))
            
            history_data = {
                'namespace': self.namespace,
                'export_timestamp': datetime.now().isoformat(),
                'messages': []
            }
            
            for row in cursor.fetchall():
                timestamp, role, content, tool_calls_json, sequence_number = row
                
                message_data = {
                    'timestamp': timestamp,
                    'role': role,
                    'content': content,
                    'sequence_number': sequence_number
                }
                
                if tool_calls_json:
                    try:
                        message_data['tool_calls'] = json.loads(tool_calls_json)
                    except json.JSONDecodeError:
                        pass
                
                history_data['messages'].append(message_data)
            
            conn.close()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Failed to export conversation history: {e}")
            return False
    
    def has_messages(self) -> bool:
        """Check if this namespace has any conversation history
        
        Returns:
            True if messages exist, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM conversation_history
            WHERE namespace = ?
            LIMIT 1
        """, (self.namespace,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0


def list_conversation_namespaces(db_path: str = "variables.db") -> List[str]:
    """List all available conversation namespaces
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        List of namespace strings
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT namespace
            FROM conversation_history
            ORDER BY namespace
        """)
        
        namespaces = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return namespaces
        
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        return []


def cleanup_old_conversations(db_path: str = "variables.db", days_old: int = 30):
    """Clean up conversations older than specified days
    
    Args:
        db_path: Path to SQLite database file
        days_old: Delete conversations older than this many days
    """
    from datetime import timedelta
    
    cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM conversation_history
        WHERE timestamp < ?
    """, (cutoff_date,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Cleaned up {deleted_count} old conversation messages")