import inspect

from features.task_validator import get_task_enum_name
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from widgets.ui_factory import UIComponentFactory


class ParameterConfiguration(QWidget):
    def __init__(self, task_dictionary, parent=None, task_enum=None):
        super().__init__(parent)
        self.task_dictionary = task_dictionary
        self.task_enum = task_enum
        self.widget_cache = {}  # Cache for configurations
        self.stacked_widget = QStackedWidget(self)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.stacked_widget)

    def updateUI(self, device, task_name):
        cache_key = (device, task_name)
        if cache_key not in self.widget_cache:
            task_func = self.task_dictionary.get(device, {}).get(task_name)
            spec = self._infer_ui_spec_from_function(task_func)
            container_widget = self.generateUI(spec)
            self.widget_cache[cache_key] = container_widget
            self.stacked_widget.addWidget(container_widget)

        self.stacked_widget.setCurrentWidget(self.widget_cache[cache_key])

    def _infer_ui_spec_from_function(self, func):
        # This function infers the UI specification from the function's parameter constraints
        spec = []
        sig = inspect.signature(func)
        param_types = {name: param.annotation for name, param in sig.parameters.items()}
        if hasattr(func, "param_constraints"):
            param_constraints = getattr(func, "param_constraints", {})
            for param, constraint in constraints.items():
                expected_type = param_types.get(
                    param, str
                )  # Default to str if not found
                UIComponentFactory.create_widget(
                    param,
                    constraint[0],
                    expected_type,
                    {"min": constraint[0], "max": constraint[1]},
                )
                if isinstance(constraint, tuple) and len(constraint) == 2:
                    if all(isinstance(x, int) for x in constraint):
                        # Integer range
                        spec.append(
                            UIComponentFactory.create_widget(
                                param,
                                constraint[0],
                                int,
                                {"min": constraint[0], "max": constraint[1]},
                            )
                        )
                    elif any(isinstance(x, float) for x in constraint):
                        # Float range
                        spec.append(
                            UIComponentFactory.create_widget(
                                param,
                                constraint[0],
                                float,
                                {"min": constraint[0], "max": constraint[1]},
                            )
                        )
                elif isinstance(constraint, bool):
                    # Boolean checkbox
                    spec.append(
                        UIComponentFactory.create_widget(param, constraint, bool)
                    )
                # Add more cases as necessary
        return spec

    def generateUI(self, spec):
        container = QWidget()
        layout = QVBoxLayout(container)
        for widget in spec:
            layout.addWidget(
                widget
            )  # Directly add the widget returned by UIComponentFactory
        container.setLayout(layout)
        return container

    def getUserData(self, task_spec):
        parameters = {}
        current_container = (
            self.stacked_widget.currentWidget()
        )  # Get the currently visible container
        if not current_container:
            return parameters  # Return empty if no container is visible

        for spec in task_spec:
            kwarg_label = spec.get("kwarg_label", spec.get("label"))
            # Now iterate through the current container's layout to find the widget
            layout = current_container.layout()
            for i in range(layout.count()):
                layout_item = layout.itemAt(i)
                widget = layout_item.widget()
                if isinstance(widget, QLabel) and widget.text() == spec["label"]:
                    # Assuming input widget is next in the layout after its label
                    input_widget = (
                        layout.itemAt(i + 1).widget()
                        if i + 1 < layout.count()
                        else None
                    )
                    if input_widget:
                        value = self.extractValue(input_widget, spec)
                        if value is not None:  # Only add if extraction was successful
                            parameters[kwarg_label] = value
                    break  # Break after finding the widget to avoid unnecessary iterations

        return parameters

    def getConfiguration(self, task_spec):
        """
        Collects the validated configuration from the UI and prepares it for use or saving.
        """
        # Extract the user-modified configuration from the UI elements
        data = self.getUserData(task_spec)

        # Validate the extracted data
        # valid, message = self.validate(data) TODO
        # if not valid:
        #     QMessageBox.critical(self, "Validation Error", message)
        #     raise ValueError("Configuration validation failed.")

        return data

    def extractValue(self, widget, spec):
        if isinstance(widget, QLineEdit):
            value = widget.text()
        elif isinstance(widget, QComboBox):
            value = widget.currentText()
        else:
            value = None

        # Correctly cast the value based on its data type
        if spec.get("data_type") == "int":
            try:
                return int(value)
            except ValueError:
                # Handle invalid int conversion
                return None
        elif spec.get("data_type") == "float":
            try:
                return float(value)
            except ValueError:
                # Handle invalid float conversion
                return None
        elif spec.get("data_type") == "str":
            return str(value)
        elif spec.get("data_type") == "bool":
            # Assuming that boolean values are represented by specific strings (e.g., "ON" or "OFF")
            return value.lower() in ["true", "1", "t", "y", "yes", "ok", "on"]
        else:
            return value
