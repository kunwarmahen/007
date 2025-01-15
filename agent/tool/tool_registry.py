import inspect
from dataclasses import dataclass
from typing import _GenericAlias
from typing import Callable, Any, Dict, get_type_hints, Optional

@dataclass
class Tool:
    name: str
    description: str
    func: Callable[..., str]
    arguments: Dict[str, Dict[str, str]]
    
    def __call__(self, *args, **kwargs) -> str:
        return self.func(*args, **kwargs)

def parse_docstring_params(docstring: str) -> Dict[str, str]:
    """Extract parameter descriptions from docstring."""
    if not docstring:
        return {}
    
    params = {}
    lines = docstring.split('\n')
    in_params = False
    current_param = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Args:'):
            in_params = True
        elif in_params:
            if line.startswith('-') or line.startswith('*'):
                current_param = line.lstrip('- *').split(':')[0].strip()
                params[current_param] = line.lstrip('- *').split(':')[1].strip()
            elif current_param and line:
                params[current_param] += ' ' + line.strip()
            elif not line:
                in_params = False
    
    return params

def get_type_description(type_hint: Any) -> str:
    """Get a human-readable description of a type hint."""
    if isinstance(type_hint, _GenericAlias):
        if type_hint._name == 'Literal':
            return f"one of {type_hint.__args__}"
    return type_hint.__name__

def tool(name: str = None):
    def decorator(func: Callable[..., str]) -> Tool:
        tool_name = name or func.__name__
        description = inspect.getdoc(func) or "No description available"
        
        type_hints = get_type_hints(func)
        param_docs = parse_docstring_params(description)
        sig = inspect.signature(func)
        
        params = {}
        for param_name, param in sig.parameters.items():
            params[param_name] = {
                "type": get_type_description(type_hints.get(param_name, Any)),
                "description": param_docs.get(param_name, "No description available")
            }
        
        return Tool(
            name=tool_name,
            description=description.split('\n\n')[0],
            func=func,
            arguments=params
        )
    return decorator