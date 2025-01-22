import time
from functools import wraps

def time_execution(method):
    """
    A decorator to measure and print the execution time of a function in a class.
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time for {method.__name__}: {end_time - start_time:.6f} seconds")
        return result
    return wrapper

# Example usage within a class:
class ExampleClass:
    @time_execution
    def example_method(self, n):
        total = 0
        for i in range(n):
            total += i
        print(total)
        return total

# Usage
obj = ExampleClass()
result = obj.example_method(10**6)
