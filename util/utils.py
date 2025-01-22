from agent.blog.blog_agent import BlogAgent
from agent.generic.generic_agent import GenericAgent
from agent.tool.tool_agent import ToolAgent
from agent.interactive.interactive_agent import InteractiveAgent


# Generic function to call a method dynamically
def invoke_agent(class_name, method_name, *args, **kwargs):
    # Check if the class exists
    if class_name in globals():
        cls = globals()[class_name]  # Get the class from global scope
        obj = cls()  # Instantiate the class
        if hasattr(obj, method_name):  # Check if the method exists
            method = getattr(obj, method_name)  # Get the method
            print(f"Invoking agent: '{cls.__name__}'")
            return method(*args, **kwargs)  # Call the method
        else:
            raise AttributeError(f"'{class_name}' object has no method '{method_name}'")
    else:
        raise NameError(f"Class '{class_name}' is not defined.")


# def invoke_agent(class_name, method_name, init_args=None, init_kwargs=None, *args, **kwargs):
#     # init_args = init_args or []  # Default to empty list if not provided
#     # init_kwargs = init_kwargs or {}  # Default to empty dict if not provided
    
#     print(class_name)
#     print(method_name)
#     print(init_args)
#     print(init_kwargs)
#     print(args)
#     print(kwargs)
#     # Check if the class exists
#     if class_name in globals():
#         cls = globals()[class_name]  # Get the class from the global scope
#         if init_args and init_kwargs:
#             obj = cls(*init_args, **init_kwargs)  # Instantiate the class with init arguments
#         else:
#             obj = cls() 
#         if hasattr(obj, method_name):  # Check if the method exists
#             method = getattr(obj, method_name)  # Get the method
#             return method(*args, **kwargs)  # Call the method with arguments
#         else:
#             raise AttributeError(f"'{class_name}' object has no method '{method_name}'")
#     else:
#         raise NameError(f"Class '{class_name}' is not defined.")