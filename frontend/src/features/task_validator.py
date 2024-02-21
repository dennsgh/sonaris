import inspect
from typing import Any, Callable, Dict, List, Tuple


def is_type_compatible(expected_type, value) -> bool:
    """
    Checks if the provided value is compatible with the expected type,
    applying custom validation rules and handling unannotated parameters.
    """
    # Handle None values (for optional parameters)
    if value is None:
        return True

    # Default unannotated parameters to str
    if expected_type is inspect.Parameter.empty:
        expected_type = str

    # Custom handling for bool to ensure strict type matching
    if expected_type is bool:
        return isinstance(value, bool)

    # Allow int values for float parameters
    if expected_type is float and isinstance(value, int):
        return True

    # Treat everything as compatible with str
    if expected_type is str:
        return True

    # Check for direct type compatibility or instance of custom classes
    if isinstance(value, expected_type):
        return True

    # Handle complex types like lists, dicts by checking type only (not contents)
    if expected_type in [list, dict] and type(value) is expected_type:
        return True

    # Further validation for the contents of lists, dicts, or custom classes could be added here

    return False


def validate_task_parameters(
    task_function, parameters: Dict[str, Any]
) -> Tuple[bool, str]:
    sig = inspect.signature(task_function)
    missing_params = []
    extra_params = []
    type_mismatches = []

    for name, param in sig.parameters.items():
        expected_type = param.annotation
        provided_value = parameters.get(name, inspect.Parameter.empty)

        if provided_value is inspect.Parameter.empty:
            if param.default is inspect.Parameter.empty:  # Required parameter
                missing_params.append(name)
        else:
            if (
                not is_type_compatible(expected_type, provided_value)
                and expected_type is not inspect.Parameter.empty
            ):
                type_mismatches.append((name, type(provided_value), expected_type))

    for name in parameters:
        if name not in sig.parameters:
            extra_params.append(name)

    if missing_params or extra_params or type_mismatches:
        messages = []
        if missing_params:
            messages.append(f"Missing required params: {', '.join(missing_params)}.")
        if extra_params:
            messages.append(f"Extra params provided: {', '.join(extra_params)}.")
        if type_mismatches:
            mismatch_details = ", ".join(
                [
                    f"{name} (got {got.__name__}, expected {expected.__name__})"
                    for name, got, expected in type_mismatches
                ]
            )
            messages.append(f"Type mismatches: {mismatch_details}.")
        return False, "Validation failed: " + " ".join(messages)

    return True, "All parameters are valid."


def validate_configuration(
    config: Dict[str, Any], task_functions: Dict[str, Callable]
) -> List[Tuple[str, bool, str]]:
    results = []
    for step in config.get("experiment", {}).get("steps", []):
        task_name = step.get("task")
        if task_name in task_functions:
            is_valid, message = validate_task_parameters(
                task_functions[task_name], step.get("parameters", [{}])[0]
            )
            results.append((task_name, is_valid, message))
        else:
            results.append((task_name, False, "Task function not found."))
    return results
