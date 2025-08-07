#!/usr/bin/env python3
"""Natural Language Macro Interpreter

Simple and robust Python orchestrator for natural language macros.
Handles session management, namespace system, and OpenAI-compatible API integration.
"""

import os
import sys
import uuid
import argparse
import json
import re
from openai import OpenAI
from variable_db import VariableDB
from variable_history import VariableHistoryManager


class NLMSession:
    """Natural Language Macro Session Manager"""
    
    def __init__(self, namespace=None, model=None, endpoint=None, api_key="ollama"):
        """Initialize NLM session
        
        Args:
            namespace: Session namespace (auto-generated UUID if None)
            model: OpenAI model name (uses default if None)
            endpoint: API endpoint (uses default if None)  
            api_key: API key (defaults to "ollama")
        """
        self.namespace = namespace or str(uuid.uuid4())[:8]
        self.model = model or "gpt-oss:20b"
        self.endpoint = endpoint or "http://localhost:1234/v1"  # LMStudio default for better performance
        
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=api_key
        )
        
        # Initialize variable management
        self.variable_db = VariableDB("variables.db")
        self.history_manager = VariableHistoryManager("variables.db")
        
        # System prompt for natural language macro execution
        self.system_prompt = """You are a natural language macro interpreter.

VARIABLE SYNTAX RULES:
1. Session variables: {{variable_name}} - stored in current session namespace
2. Global variables: {{@variable_name}} - stored globally, accessible by all sessions
3. Other session variables: {{session_name.variable}} - access variables from other sessions

IMPORTANT SYNTAX EXAMPLES:
- Save 'value' to {{@config}} → save_variable("@config", "value") for global variable
- Save 'data' to {{local_var}} → save_variable("local_var", "value") for session variable  
- Get {{@environment}} → get_variable("@environment") for global variable
- Get {{other_session.data}} → get_variable("other_session.data") for cross-session access

TOOL USAGE RULES:
1. When user says "Save X to {{@var}}", use save_variable tool with name="@var" and value="X"
2. When user says "Save X to {{var}}", use save_variable tool with name="var" and value="X"
3. When user says "Get {{@var}}" or mentions {{@var}}, use get_variable tool with name="@var"
4. When user says "Get {{var}}" or mentions {{var}}, use get_variable tool with name="var"
5. When user says "Delete {{@var}}" or "Delete {{var}}", use delete_variable tool appropriately
6. When user says "Delete all variables" or "Clear all variables", use delete_all_variables tool
7. When user says "List variables", use list_variables tool

RESPONSE FORMAT:
- Always respond with clear, natural language
- Explain what you did or any issues encountered
- Be concise but informative
- When referring to variables in responses, use correct {{variable}} or {{@variable}} format

Available tools: save_variable, get_variable, list_variables, delete_variable, delete_all_variables"""

    def _resolve_variable_name(self, variable_name):
        """Resolve variable name with namespace
        
        Args:
            variable_name: Variable name (may include namespace or @ prefix)
            
        Returns:
            Resolved variable name with namespace
        """
        # Handle global variables with @ prefix
        if variable_name.startswith("@"):
            # Convert @variable to global.variable
            return f"global.{variable_name[1:]}"
        elif "." in variable_name:
            # Already has namespace (e.g., global.var, session.var)
            return variable_name
        else:
            # Session variable
            return f"{self.namespace}.{variable_name}"
    
    def _expand_variables(self, text):
        """Expand {{variable}} and {{@variable}} references in text
        
        Args:
            text: Text containing {{variable}} and {{@variable}} references
            
        Returns:
            Text with variables expanded to their values
        """
        def replace_variable(match):
            var_name = match.group(1)  # Extract variable name from {{var_name}} or {{@var_name}}
            resolved_name = self._resolve_variable_name(var_name)
            value = self.variable_db.get_variable(resolved_name)
            
            if value is not None and value != "":
                return value
            else:
                # Keep original {{var_name}} or {{@var_name}} if variable doesn't exist
                return match.group(0)
        
        # Pattern to match {{variable_name}} and {{@variable_name}} including namespace variants
        pattern = r'\{\{(@?[^}]+)\}\}'
        expanded_text = re.sub(pattern, replace_variable, text)
        return expanded_text
    
    def _save_variable_tool(self, name, value):
        """Tool function: Save variable"""
        resolved_name = self._resolve_variable_name(name)
        
        # Get old value for history
        old_value = self.variable_db.get_variable(resolved_name)
        
        # Save variable
        self.variable_db.save_variable(resolved_name, value)
        
        # Log to history
        namespace = resolved_name.split(".", 1)[0] if "." in resolved_name else "unknown"
        var_name = resolved_name.split(".", 1)[1] if "." in resolved_name else resolved_name
        self.history_manager.log_change(namespace, var_name, old_value, value)
        
        return f"Successfully saved '{value}' to variable '{resolved_name}'"
    
    def _get_variable_tool(self, name):
        """Tool function: Get variable"""
        resolved_name = self._resolve_variable_name(name)
        value = self.variable_db.get_variable(resolved_name)
        
        if value is not None and value != "":
            return f"Variable '{resolved_name}' contains: {value}"
        else:
            return f"Variable '{resolved_name}' not found"
    
    def _list_variables_tool(self):
        """Tool function: List variables"""
        variables = self.variable_db.list_variables()
        if variables:
            var_list = []
            for name, value in variables.items():
                var_list.append(f"{name} = {value}")
            return "Variables:\n" + "\n".join(var_list)
        else:
            return "No variables found"
    
    def _delete_variable_tool(self, name):
        """Tool function: Delete variable"""
        resolved_name = self._resolve_variable_name(name)
        
        # Get old value for history
        old_value = self.variable_db.get_variable(resolved_name)
        
        if old_value is not None:
            success = self.variable_db.delete_variable(resolved_name)
            if success:
                # Log deletion to history
                namespace = resolved_name.split(".", 1)[0] if "." in resolved_name else "unknown"
                var_name = resolved_name.split(".", 1)[1] if "." in resolved_name else resolved_name
                self.history_manager.log_change(namespace, var_name, old_value, None)
                
                return f"Successfully deleted variable '{resolved_name}'"
            else:
                return f"Failed to delete variable '{resolved_name}'"
        else:
            return f"Variable '{resolved_name}' not found"
    
    def _delete_all_variables_tool(self):
        """Tool function: Delete all variables"""
        variables = self.variable_db.list_variables()
        if not variables:
            return "No variables found to delete"
        
        deleted_count = 0
        deleted_vars = []
        
        for name in variables.keys():
            old_value = variables[name]
            success = self.variable_db.delete_variable(name)
            if success:
                # Log deletion to history
                namespace = name.split(".", 1)[0] if "." in name else "unknown"
                var_name = name.split(".", 1)[1] if "." in name else name
                self.history_manager.log_change(namespace, var_name, old_value, None)
                
                deleted_count += 1
                deleted_vars.append(name)
        
        return f"Successfully deleted {deleted_count} variables: {', '.join(deleted_vars)}"

    def _get_tools_definition(self):
        """Get OpenAI tools definition"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "save_variable",
                    "description": "Save a value to a variable with namespace support",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Variable name (with or without namespace)"
                            },
                            "value": {
                                "type": "string", 
                                "description": "Value to save"
                            }
                        },
                        "required": ["name", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_variable",
                    "description": "Get a variable value with namespace support",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Variable name (with or without namespace)"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_variables",
                    "description": "List all variables in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_variable",
                    "description": "Delete a variable with namespace support",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Variable name (with or without namespace)"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_all_variables",
                    "description": "Delete all variables in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def _execute_tool_call(self, tool_call):
        """Execute a tool call and return result"""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        if function_name == "save_variable":
            return self._save_variable_tool(arguments["name"], arguments["value"])
        elif function_name == "get_variable":
            return self._get_variable_tool(arguments["name"])
        elif function_name == "list_variables":
            return self._list_variables_tool()
        elif function_name == "delete_variable":
            return self._delete_variable_tool(arguments["name"])
        elif function_name == "delete_all_variables":
            return self._delete_all_variables_tool()
        else:
            return f"Unknown function: {function_name}"

    def execute(self, macro_content):
        """Execute natural language macro content
        
        Args:
            macro_content: String containing macro instructions
            
        Returns:
            String result from macro execution
        """
        try:
            # First expand any existing variables in the macro content
            expanded_content = self._expand_variables(macro_content)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Execute this macro:\n\n{expanded_content}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools_definition(),
                max_tokens=1000
            )
            
            message = response.choices[0].message
            result_parts = []
            
            # Handle tool calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_result = self._execute_tool_call(tool_call)
                    result_parts.append(tool_result)
            
            # Add assistant response
            if message.content:
                result_parts.append(message.content)
            
            return "\n".join(result_parts) if result_parts else "Macro executed (no output)"
            
        except Exception as e:
            return f"Error executing macro: {str(e)}"
    
    # User-friendly variable API
    def save(self, key, value):
        """Save a variable in this session's namespace, or global if key starts with @
        
        Args:
            key: Variable name (use @key for global variables)
            value: Variable value
            
        Returns:
            Full variable name that was saved
        """
        if key.startswith("@"):
            # Global variable: @key -> global:key
            clean_key = key[1:]  # Remove @ prefix
            full_key = f"global:{clean_key}"
            namespace = "global"
            log_key = clean_key
        else:
            # Local variable: key -> namespace:key
            full_key = f"{self.namespace}:{key}"
            namespace = self.namespace
            log_key = key
        
        old_value = self.variable_db.get_variable(full_key)
        self.variable_db.save_variable(full_key, str(value))
        
        # Log to history if enabled
        self.history_manager.log_change(namespace, log_key, old_value, str(value))
        
        return full_key
    
    def get(self, key):
        """Get a variable from this session's namespace, or global if key starts with @
        
        Args:
            key: Variable name (use @key for global variables)
            
        Returns:
            Variable value or None if not found
        """
        if key.startswith("@"):
            # Global variable: @key -> global:key
            clean_key = key[1:]  # Remove @ prefix
            full_key = f"global:{clean_key}"
        else:
            # Local variable: key -> namespace:key
            full_key = f"{self.namespace}:{key}"
        
        return self.variable_db.get_variable(full_key)
    
    def delete(self, key):
        """Delete a variable from this session's namespace, or global if key starts with @
        
        Args:
            key: Variable name (use @key for global variables)
            
        Returns:
            True if deleted, False if not found
        """
        if key.startswith("@"):
            # Global variable: @key -> global:key
            clean_key = key[1:]  # Remove @ prefix
            full_key = f"global:{clean_key}"
            namespace = "global"
            log_key = clean_key
        else:
            # Local variable: key -> namespace:key
            full_key = f"{self.namespace}:{key}"
            namespace = self.namespace
            log_key = key
        
        old_value = self.variable_db.get_variable(full_key)
        
        if old_value is not None:
            success = self.variable_db.delete_variable(full_key)
            if success:
                # Log to history if enabled
                self.history_manager.log_change(namespace, log_key, old_value, None)
            return success
        return False
    
    def save_global(self, key, value):
        """Save a global variable accessible by all sessions
        
        Args:
            key: Variable name (without namespace)
            value: Variable value
            
        Returns:
            Full variable name that was saved
        """
        full_key = f"global:{key}"
        old_value = self.variable_db.get_variable(full_key)
        self.variable_db.save_variable(full_key, str(value))
        
        # Log to history if enabled
        self.history_manager.log_change("global", key, old_value, str(value))
        
        return full_key
    
    def get_global(self, key):
        """Get a global variable
        
        Args:
            key: Variable name (without namespace)
            
        Returns:
            Variable value or None if not found
        """
        full_key = f"global:{key}"
        return self.variable_db.get_variable(full_key)
    
    def delete_global(self, key):
        """Delete a global variable
        
        Args:
            key: Variable name (without namespace)
            
        Returns:
            True if deleted, False if not found
        """
        full_key = f"global:{key}"
        old_value = self.variable_db.get_variable(full_key)
        
        if old_value is not None:
            success = self.variable_db.delete_variable(full_key)
            if success:
                # Log to history if enabled
                self.history_manager.log_change("global", key, old_value, None)
            return success
        return False
    
    def list_local(self):
        """List all variables in this session's namespace
        
        Returns:
            Dict of variable names (without namespace) to values
        """
        all_vars = self.variable_db.list_variables()
        prefix = f"{self.namespace}:"
        local_vars = {}
        
        for full_key, value in all_vars.items():
            if full_key.startswith(prefix):
                key = full_key[len(prefix):]  # Remove namespace prefix
                local_vars[key] = value
                
        return local_vars
    
    def list_global(self):
        """List all global variables
        
        Returns:
            Dict of global variable names (without namespace) to values
        """
        all_vars = self.variable_db.list_variables()
        prefix = "global:"
        global_vars = {}
        
        for full_key, value in all_vars.items():
            if full_key.startswith(prefix):
                key = full_key[len(prefix):]  # Remove namespace prefix
                global_vars[key] = value
                
        return global_vars
    
    def clear_local(self):
        """Clear all variables in this session's namespace
        
        Returns:
            Number of variables deleted
        """
        all_vars = self.variable_db.list_variables()
        prefix = f"{self.namespace}:"
        count = 0
        
        for full_key in list(all_vars.keys()):
            if full_key.startswith(prefix):
                if self.variable_db.delete_variable(full_key):
                    count += 1
                    # Log to history if enabled
                    key = full_key[len(prefix):]
                    self.history_manager.log_change(self.namespace, key, all_vars[full_key], None)
        
        return count


def nlm_execute(macro_content, namespace=None, model=None, endpoint=None):
    """Simple function interface for macro execution
    
    Args:
        macro_content: String containing macro instructions
        namespace: Optional session namespace
        model: Optional model name
        endpoint: Optional API endpoint
        
    Returns:
        String result from macro execution
    """
    session = NLMSession(namespace=namespace, model=model, endpoint=endpoint)
    return session.execute(macro_content)


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Natural Language Macro Interpreter")
    parser.add_argument("macro_content", nargs="?", help="Macro content to execute")
    parser.add_argument("-f", "--file", help="Read macro from file")
    parser.add_argument("-n", "--namespace", help="Session namespace")
    parser.add_argument("-m", "--model", default="gpt-oss:20b", help="Model name (default: gpt-oss:20b)")
    parser.add_argument("-e", "--endpoint", default="http://localhost:1234/v1", help="API endpoint (default: LMStudio http://localhost:1234/v1)")
    parser.add_argument("--list-sessions", action="store_true", help="List available sessions")
    
    args = parser.parse_args()
    
    # Override with environment variables if available
    model = os.getenv("NLM_MODEL", args.model)
    endpoint = os.getenv("NLM_ENDPOINT", args.endpoint)
    
    if args.list_sessions:
        # List sessions from variable database
        db = VariableDB("variables.db")
        variables = db.list_variables()
        namespaces = set()
        for var_name in variables.keys():
            if "." in var_name:
                namespace = var_name.split(".", 1)[0]
                namespaces.add(namespace)
        
        if namespaces:
            print("Available sessions:")
            for ns in sorted(namespaces):
                print(f"  {ns}")
        else:
            print("No sessions found")
        return
    
    # Get macro content
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Process each line as a separate macro
            session = NLMSession(namespace=args.namespace, model=model, endpoint=endpoint)
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                # Skip empty lines and markdown headers/comments
                if not line or line.startswith('#') or line.startswith('Execute this file'):
                    continue
                
                print(f"Executing line {line_num}: {line}")
                try:
                    result = session.execute(line)
                    print(f"Result: {result}")
                    
                    # Debug: Check if variables were actually saved
                    if "save" in line.lower() and "{{" in line:
                        variables = session.variable_db.list_variables()
                        recent_vars = {k: v for k, v in variables.items() if session.namespace in k}
                        print(f"Debug - Current session variables: {recent_vars}")
                    
                    print("-" * 50)
                except Exception as e:
                    print(f"Error on line {line_num}: {e}")
                    print("-" * 50)
                    
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    elif args.macro_content:
        macro_content = args.macro_content
        # Execute single macro
        result = nlm_execute(macro_content, args.namespace, model, endpoint)
        print(result)
    else:
        print("Error: Provide macro content or use -f to read from file")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()