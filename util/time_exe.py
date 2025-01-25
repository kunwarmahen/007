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
        class_name = args[0].__class__.__name__ if args else None
        if class_name:
            print(f"Execution time for {class_name}.{method.__name__}: {end_time - start_time:.6f} seconds")
        else:
            print(f"Execution time for {method.__name__}: {end_time - start_time:.6f} seconds")
        
        return result
    return wrapper