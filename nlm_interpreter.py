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
    
    # Constants for namespace handling
    NAMESPACE_SEPARATOR = ":"
    GLOBAL_PREFIX = "global"
    AT_PREFIX = "@"
    
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
        self.system_prompt = """You are a natural language macro interpreter that processes {{variable}} syntax.

VARIABLE SYNTAX RULES:
1. Session variables: {{variable_name}} - stored in current session namespace  
2. Global variables: {{@variable_name}} - stored globally, accessible by all sessions
3. Other session variables: {{session_name.variable}} - access variables from other sessions

CRITICAL: Variables are NOT pre-expanded. You receive raw {{variable}} syntax and must decide whether to read or write.

VARIABLE USAGE PATTERNS:
1. **Variable Assignment/Update**:
   - "{{name}} is Alice" → save_variable("name", "Alice")
   - "Save X to {{var}}" → save_variable("var", "X")  
   - "Set {{@status}} to ready" → save_variable("@status", "ready")
   - "Update {{counter}} to 10" → save_variable("counter", "10")

2. **Variable Reference/Reading**:
   - "Show me {{name}}" → get_variable("name") first, then respond
   - "Print {{@config}}" → get_variable("@config") first, then display
   - "If {{status}} is ready, then..." → get_variable("status") first to check

3. **Mixed Operations**:
   - "Add 5 to {{counter}}" → get_variable("counter"), calculate, then save_variable("counter", new_value)
   - "Change {{name}} from Alice to Bob" → save_variable("name", "Bob")

DECISION LOGIC:
- If {{variable}} appears in assignment context → use save_variable
- If {{variable}} needs its value for processing → use get_variable first
- When in doubt, analyze the intent: is the user setting or using the variable?

MULTI-STEP OPERATIONS:
- For complex operations requiring multiple steps, execute ALL necessary tools in sequence
- Example: "Combine {{a}} and {{b}} and save to {{c}}" → get_variable("a"), get_variable("b"), then save_variable("c", combined_result)
- Do not just describe the steps - EXECUTE them by calling the appropriate tools
- Complete the entire operation before responding to the user

RESPONSE FORMAT:
- Always respond with clear, natural language
- Explain what you did or any issues encountered
- Be concise but informative
- When referring to variables in responses, use correct {{variable}} or {{@variable}} format

Available tools: save_variable, get_variable, list_variables, delete_variable, delete_all_variables"""

    # Tools definition for OpenAI API
    TOOLS_DEFINITION = [
        {
            "type": "function",
            "function": {
                "name": "save_variable",
                "description": "Save a value to a variable with namespace support",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Variable name (with or without namespace)"},
                        "value": {"type": "string", "description": "Value to save"}
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
                        "name": {"type": "string", "description": "Variable name (with or without namespace)"}
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
                "parameters": {"type": "object", "properties": {}, "required": []}
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
                        "name": {"type": "string", "description": "Variable name (with or without namespace)"}
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
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        }
    ]

    def _parse_key_with_namespace(self, key):
        """Parse key and return full_key, namespace, and clean_key for logging
        
        Args:
            key: Variable name (may include @ prefix)
            
        Returns:
            tuple: (full_key, namespace, log_key)
        """
        if key.startswith(self.AT_PREFIX):
            # Global variable: @key -> global:key
            clean_key = key[1:]  # Remove @ prefix
            full_key = f"{self.GLOBAL_PREFIX}{self.NAMESPACE_SEPARATOR}{clean_key}"
            namespace = self.GLOBAL_PREFIX
            log_key = clean_key
        else:
            # Local variable: key -> namespace:key
            full_key = f"{self.namespace}{self.NAMESPACE_SEPARATOR}{key}"
            namespace = self.namespace
            log_key = key
        
        return full_key, namespace, log_key

    def _split_full_key(self, full_key):
        """Split full key into namespace and variable name
        
        Args:
            full_key: Full variable name with namespace
            
        Returns:
            tuple: (namespace, var_name)
        """
        if self.NAMESPACE_SEPARATOR in full_key:
            return full_key.split(self.NAMESPACE_SEPARATOR, 1)
        return "unknown", full_key

    def _log_variable_change(self, full_key, old_value, new_value):
        """Log variable change to history
        
        Args:
            full_key: Full variable name with namespace
            old_value: Previous value
            new_value: New value
        """
        namespace, var_name = self._split_full_key(full_key)
        self.history_manager.log_change(namespace, var_name, old_value, new_value)

    def _resolve_variable_name(self, variable_name):
        """Resolve variable name with namespace (legacy method for backward compatibility)
        
        Args:
            variable_name: Variable name (may include namespace or @ prefix)
            
        Returns:
            Resolved variable name with namespace
        """
        # Handle global variables with @ prefix
        if variable_name.startswith(self.AT_PREFIX):
            # Convert @variable to global:variable
            return f"{self.GLOBAL_PREFIX}{self.NAMESPACE_SEPARATOR}{variable_name[1:]}"
        elif self.NAMESPACE_SEPARATOR in variable_name or "." in variable_name:
            # Already has namespace (e.g., global:var, session:var, or legacy global.var)
            # Convert legacy dot format to colon format if needed
            if "." in variable_name and self.NAMESPACE_SEPARATOR not in variable_name:
                namespace, var_name = variable_name.split(".", 1)
                return f"{namespace}{self.NAMESPACE_SEPARATOR}{var_name}"
            return variable_name
        else:
            # Session variable
            return f"{self.namespace}{self.NAMESPACE_SEPARATOR}{variable_name}"
    
    def _expand_variables(self, text):
        """Expand {{variable}} and {{@variable}} references in text
        
        NOTE: This method is kept for testing purposes and backward compatibility.
        It is NOT used in the main execution flow since we now pass raw {{variable}}
        syntax directly to the LLM for proper context-aware processing.
        
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
                self._log_variable_change(name, old_value, None)
                deleted_count += 1
                deleted_vars.append(name)
        
        return f"Successfully deleted {deleted_count} variables: {', '.join(deleted_vars)}"

    def _execute_tool_call(self, tool_call):
        """Execute a tool call and return result"""
        try:
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
                
        except json.JSONDecodeError as e:
            return f"Error parsing tool arguments for {function_name}: {str(e)}"
        except KeyError as e:
            return f"Missing required argument for {function_name}: {str(e)}"
        except Exception as e:
            return f"Error executing tool {function_name}: {str(e)}"

    def execute(self, macro_content):
        """Execute natural language macro content with multi-turn tool support
        
        Args:
            macro_content: String containing macro instructions
            
        Returns:
            String result from macro execution
        """
        try:            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Execute this macro:\n\n{macro_content}"}
            ]
            
            max_turns = 10  # Allow more complex operations while preventing infinite loops
            turn = 0
            all_results = []
            
            while turn < max_turns:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.TOOLS_DEFINITION,
                    max_tokens=1000
                )
                
                message = response.choices[0].message
                
                # Handle tool calls
                if message.tool_calls:
                    tool_results = []
                    for tool_call in message.tool_calls:
                        tool_result = self._execute_tool_call(tool_call)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": tool_result
                        })
                        all_results.append(tool_result)
                    
                    # Add assistant message and tool results to conversation
                    messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})
                    messages.extend(tool_results)
                    
                    turn += 1
                    continue
                else:
                    # No more tool calls, add final response
                    if message.content:
                        all_results.append(message.content)
                    break
            
            return "\n".join(all_results) if all_results else "Macro executed (no output)"
            
        except json.JSONDecodeError as e:
            return f"Error parsing tool arguments: {str(e)}"
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
        full_key, namespace, log_key = self._parse_key_with_namespace(key)
        
        old_value = self.variable_db.get_variable(full_key)
        self.variable_db.save_variable(full_key, str(value))
        
        # Log to history if enabled
        self._log_variable_change(full_key, old_value, str(value))
        
        return full_key
    
    def get(self, key):
        """Get a variable from this session's namespace, or global if key starts with @
        
        Args:
            key: Variable name (use @key for global variables)
            
        Returns:
            Variable value or None if not found
        """
        full_key, _, _ = self._parse_key_with_namespace(key)
        return self.variable_db.get_variable(full_key)
    
    def delete(self, key):
        """Delete a variable from this session's namespace, or global if key starts with @
        
        Args:
            key: Variable name (use @key for global variables)
            
        Returns:
            True if deleted, False if not found
        """
        full_key, _, _ = self._parse_key_with_namespace(key)
        old_value = self.variable_db.get_variable(full_key)
        
        if old_value is not None:
            success = self.variable_db.delete_variable(full_key)
            if success:
                # Log to history if enabled
                self._log_variable_change(full_key, old_value, None)
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
        full_key = f"{self.GLOBAL_PREFIX}{self.NAMESPACE_SEPARATOR}{key}"
        old_value = self.variable_db.get_variable(full_key)
        self.variable_db.save_variable(full_key, str(value))
        
        # Log to history if enabled
        self._log_variable_change(full_key, old_value, str(value))
        
        return full_key
    
    def get_global(self, key):
        """Get a global variable
        
        Args:
            key: Variable name (without namespace)
            
        Returns:
            Variable value or None if not found
        """
        full_key = f"{self.GLOBAL_PREFIX}{self.NAMESPACE_SEPARATOR}{key}"
        return self.variable_db.get_variable(full_key)
    
    def delete_global(self, key):
        """Delete a global variable
        
        Args:
            key: Variable name (without namespace)
            
        Returns:
            True if deleted, False if not found
        """
        full_key = f"{self.GLOBAL_PREFIX}{self.NAMESPACE_SEPARATOR}{key}"
        old_value = self.variable_db.get_variable(full_key)
        
        if old_value is not None:
            success = self.variable_db.delete_variable(full_key)
            if success:
                # Log to history if enabled
                self._log_variable_change(full_key, old_value, None)
            return success
        return False
    
    def list_local(self):
        """List all variables in this session's namespace
        
        Returns:
            Dict of variable names (without namespace) to values
        """
        all_vars = self.variable_db.list_variables()
        prefix = f"{self.namespace}{self.NAMESPACE_SEPARATOR}"
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
        prefix = f"{self.GLOBAL_PREFIX}{self.NAMESPACE_SEPARATOR}"
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
        prefix = f"{self.namespace}{self.NAMESPACE_SEPARATOR}"
        count = 0
        
        for full_key in list(all_vars.keys()):
            if full_key.startswith(prefix):
                if self.variable_db.delete_variable(full_key):
                    count += 1
                    # Log to history if enabled
                    self._log_variable_change(full_key, all_vars[full_key], None)
        
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


def _handle_list_sessions():
    """Handle --list-sessions command"""
    db = VariableDB("variables.db")
    variables = db.list_variables()
    namespaces = set()
    
    for var_name in variables.keys():
        if NLMSession.NAMESPACE_SEPARATOR in var_name:
            namespace = var_name.split(NLMSession.NAMESPACE_SEPARATOR, 1)[0]
            namespaces.add(namespace)
    
    if namespaces:
        print("Available sessions:")
        for ns in sorted(namespaces):
            print(f"  {ns}")
    else:
        print("No sessions found")


def _execute_from_file(file_path, namespace, model, endpoint):
    """Execute macros from file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        session = NLMSession(namespace=namespace, model=model, endpoint=endpoint)
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            # Skip empty lines and markdown headers/comments
            if not line or line.startswith('#') or line.startswith('Execute this file'):
                continue
            
            print(f"Executing line {line_num}: {line}")
            try:
                result = session.execute(line)
                print(f"Result: {result}")
                print("-" * 50)
            except Exception as e:
                print(f"Error on line {line_num}: {e}")
                print("-" * 50)
                
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def _execute_single_macro(macro_content, namespace, model, endpoint):
    """Execute single macro"""
    result = nlm_execute(macro_content, namespace, model, endpoint)
    print(result)


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
        _handle_list_sessions()
        return
    
    if args.file:
        _execute_from_file(args.file, args.namespace, model, endpoint)
    elif args.macro_content:
        _execute_single_macro(args.macro_content, args.namespace, model, endpoint)
    else:
        print("Error: Provide macro content or use -f to read from file")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()