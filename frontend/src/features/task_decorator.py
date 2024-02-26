import functools


# Adjusted decorator to simply pass through functions without constraints
def parameter_constraints(**constraints):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach only if constraints are provided
        if constraints:
            wrapper.param_constraints = constraints
        return wrapper

    return decorator
