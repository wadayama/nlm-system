#!/usr/bin/env python3
"""SystemSession class for unified global variable access

Provides a cleaner, more intuitive interface for global variable operations
while maintaining full compatibility with NLMSession functionality.
"""

from nlm_interpreter import NLMSession


class SystemSession(NLMSession):
    """Global variable access optimized session
    
    Provides cleaner syntax for global variable operations with @-prefixed
    variable names to match natural language macro syntax {{@variable}}.
    Inherits all NLMSession functionality including macro execution
    and settings management.
    
    Key features:
    - Automatic @ prefix handling for global variables
    - Unified interface between Python and natural language macros
    - Full backward compatibility with existing code
    - Context manager support for clean usage
    
    Example:
        # Basic usage
        system = SystemSession()
        system.set_global("@status", "active")      # Explicit @ prefix
        system.set_global("status", "active")       # Auto @ prefix
        value = system.get_global("status")         # Returns "active"
        
        # Context manager
        with SystemSession() as system:
            system.set_global("config", "production")
            status = system.get_global("status")
    """
    
    def __init__(self, **kwargs):
        """Initialize SystemSession with fixed namespace
        
        Args:
            **kwargs: Additional arguments passed to NLMSession
                     (model, endpoint, api_key, reasoning_effort, verbosity)
        """
        # Force a known namespace for system operations
        super().__init__(namespace="system_session", **kwargs)
    
    def _ensure_at_prefix(self, key: str) -> str:
        """Ensure key has @ prefix for global variable access
        
        Args:
            key: Variable name with or without @ prefix
            
        Returns:
            Key with @ prefix guaranteed
        """
        if not key.startswith('@'):
            return f"@{key}"
        return key
    
    def _remove_at_prefix(self, key: str) -> str:
        """Remove @ prefix from key for display purposes
        
        Args:
            key: Variable name with or without @ prefix
            
        Returns:
            Key without @ prefix
        """
        if key.startswith('@'):
            return key[1:]
        return key
    
    def set_global(self, key: str, value: str) -> str:
        """Set global variable with automatic @ prefix handling
        
        Provides a cleaner interface for global variable setting that matches
        the natural language macro syntax {{@variable}}.
        
        Args:
            key: Variable name (with or without @ prefix)
            value: Value to store
            
        Returns:
            Full variable name that was saved (with namespace)
            
        Example:
            system = SystemSession()
            system.set_global("status", "ready")     # Auto @ prefix
            system.set_global("@config", "prod")     # Explicit @ prefix
        """
        key_with_prefix = self._ensure_at_prefix(key)
        return self.save(key_with_prefix, value)
    
    def get_global(self, key: str) -> str:
        """Get global variable with automatic @ prefix handling
        
        Args:
            key: Variable name (with or without @ prefix)
            
        Returns:
            Variable value or None if not found
            
        Example:
            system = SystemSession()
            value = system.get_global("status")      # Auto @ prefix
            value = system.get_global("@status")     # Explicit @ prefix
        """
        key_with_prefix = self._ensure_at_prefix(key)
        return self.get(key_with_prefix)
    
    def delete_global(self, key: str) -> bool:
        """Delete global variable with automatic @ prefix handling
        
        Args:
            key: Variable name (with or without @ prefix)
            
        Returns:
            True if deleted, False if not found
            
        Example:
            system = SystemSession()
            success = system.delete_global("temp_data")  # Auto @ prefix
        """
        key_with_prefix = self._ensure_at_prefix(key)
        return self.delete(key_with_prefix)
    
    def list_globals(self) -> dict:
        """List all global variables with clean key names
        
        Returns global variables with @ prefix removed from keys
        for easier readability and usage.
        
        Returns:
            Dict mapping clean variable names to their values
            
        Example:
            system = SystemSession()
            system.set_global("status", "ready")
            system.set_global("config", "prod")
            globals_dict = system.list_globals()
            # Returns: {"status": "ready", "config": "prod"}
        """
        # Use the inherited list_global() method
        globals_with_prefix = super().list_global()
        
        # Remove @ prefix from keys for cleaner display
        clean_globals = {}
        for key, value in globals_with_prefix.items():
            clean_key = self._remove_at_prefix(key)
            clean_globals[clean_key] = value
        
        return clean_globals
    
    def clear_globals(self) -> int:
        """Clear all global variables
        
        Returns:
            Number of global variables that were deleted
        """
        globals_dict = super().list_global()
        count = 0
        
        for key in globals_dict.keys():
            if self.delete_global(key):
                count += 1
        
        return count
    
    # Context manager support for clean usage
    def __enter__(self):
        """Enter context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        # Could add cleanup logic here if needed
        pass
    
    def get_system_info(self) -> dict:
        """Get information about the system session
        
        Returns:
            Dictionary with system session information
        """
        info = self.get_settings()
        info.update({
            "session_type": "SystemSession",
            "global_variables_count": len(self.list_globals()),
            "primary_purpose": "Global variable management"
        })
        return info
    
    def __repr__(self):
        """String representation of SystemSession"""
        global_count = len(self.list_globals())
        return f"SystemSession(globals={global_count}, model='{self.model}')"