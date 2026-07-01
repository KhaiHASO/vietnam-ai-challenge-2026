import inspect
from typing import Callable, Dict, Any, List

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str = None) -> Callable:
        """Decorator to register a tool and extract its schema."""
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            sig = inspect.signature(func)
            doc = func.__doc__ or ""
            
            # Simple docstring parser for description
            desc = doc.strip().split("\n")[0] if doc else "No description available."
            
            # Generate JSON Schema parameters
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                # Get type
                param_type = "string"
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict:
                    param_type = "object"
                elif param.annotation == list:
                    param_type = "array"
                
                properties[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
                
                # If no default value, it is required
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
                    
            self.tools[tool_name] = {
                "name": tool_name,
                "description": desc,
                "callable": func,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
            return func
        return decorator

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Returns JSON schemas for all registered tools (ready for OpenAI/Gemini/Ollama tool calling)."""
        schemas = []
        for name, data in self.tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": data["name"],
                    "description": data["description"],
                    "parameters": data["parameters"]
                }
            })
        return schemas

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a registered tool with the given arguments."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered.")
        
        func = self.tools[tool_name]["callable"]
        # Filter arguments to match function signature in case LLM passes extra garbage
        sig = inspect.signature(func)
        valid_args = {k: v for k, v in arguments.items() if k in sig.parameters}
        
        return func(**valid_args)

# Global tool registry instance
tool_registry = ToolRegistry()
