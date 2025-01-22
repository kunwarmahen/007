# Define some sample classes with and without __init__
class Calculator:
    def __init__(self, mode="standard"):
        self.mode = mode
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

class Greeter:
    def __init__(self, greeting="Hello"):
        self.greeting = greeting
    
    def greet(self, name):
        return f"{self.greeting}, {name}!"

# Generic function to call a method dynamically
def call_class_method(class_name, method_name, init_args=None, init_kwargs=None, *args, **kwargs):
    init_args = init_args or []  # Default to empty list if not provided
    init_kwargs = init_kwargs or {}  # Default to empty dict if not provided
    
    # Check if the class exists
    if class_name in globals():
        cls = globals()[class_name]  # Get the class from the global scope
        obj = cls(*init_args, **init_kwargs)  # Instantiate the class with init arguments
        if hasattr(obj, method_name):  # Check if the method exists
            method = getattr(obj, method_name)  # Get the method
            return method(*args, **kwargs)  # Call the method with arguments
        else:
            raise AttributeError(f"'{class_name}' object has no method '{method_name}'")
    else:
        raise NameError(f"Class '{class_name}' is not defined.")

# Example usage
print(call_class_method("Calculator", "add", init_kwargs={"mode": "scientific"}, a=10, b=5))  
# Output: 15
print(call_class_method("Calculator", "multiply", init_args=["advanced"], a=6, b=7))  
# Output: 42
print(call_class_method("Greeter", "greet", init_kwargs={"greeting": "Hi"}, name="Mahen"))  
# Output: Hi, Mahen!

# Error case
try:
    call_class_method("UnknownClass", "some_method")
except NameError as e:
    print(e)  # Output: Class 'UnknownClass' is not defined.

try:
    call_class_method("Calculator", "divide", init_args=["standard"], a=10, b=5)
except AttributeError as e:
    print(e)  # Output: 'Calculator' object has no method 'divide'
