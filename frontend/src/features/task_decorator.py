import functools


def label_annotation(position="top", text=""):
    """
    Decorator to annotate a function with label metadata.

    Args:
        position (str): The position of the label relative to the widget ('top', 'bottom', 'left', 'right').
        text (str): Optional text to use as the label.
    """

    def decorator(func):
        if not hasattr(func, "label_annotations"):
            func.label_annotations = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func.label_annotations[position] = text
        return wrapper

    return decorator


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
