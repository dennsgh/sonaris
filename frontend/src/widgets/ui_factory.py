from PyQt6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QSpinBox


class UIComponentFactory:
    @staticmethod
    def create_widget(param_name, value, expected_type, constraints=None):
        """Creates and returns a widget based on the expected data type and constraints, appending metadata."""
        widget = None

        if expected_type == bool:
            widget = QCheckBox()
            widget.setChecked(value)
        elif expected_type in (int, float):
            widget = QSpinBox() if expected_type == int else QDoubleSpinBox()
            min_val, max_val = -2147483647, 2147483647  # Default limits
            if constraints:
                # Apply constraints if available
                min_val, max_val = constraints.get("min", min_val), constraints.get(
                    "max", max_val
                )
            widget.setMinimum(min_val)
            widget.setMaximum(max_val)
            widget.setValue(value)
        elif expected_type == str:
            if constraints and "options" in constraints:
                # If there are specific options provided, use a combo box
                widget = QComboBox()
                widget.addItems(constraints["options"])
                widget.setCurrentText(value)
            else:
                # Default to QLineEdit for general string input
                widget = QLineEdit()
                widget.setText(value)

        # Append metadata here
        widget.setProperty("expected_type", expected_type.__name__)

        return widget

    @staticmethod
    def extract_value(widget, expected_type=None):
        """Extracts and returns the value from the widget, casting it to the expected type."""
        # Retrieve the expected type from the widget metadata if not explicitly provided
        if expected_type is None:
            expected_type_name = widget.property("expected_type")
            if expected_type_name == "bool":
                expected_type = bool
            elif expected_type_name == "int":
                expected_type = int
            elif expected_type_name == "float":
                expected_type = float
            elif expected_type_name == "str":
                expected_type = str
            else:
                expected_type = None  # Fallback if type is unknown/not set

        if isinstance(widget, QLineEdit):
            value = widget.text()
        elif isinstance(widget, QCheckBox):
            value = widget.isChecked()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            value = widget.value()
        elif isinstance(widget, QComboBox):
            value = widget.currentText()
        else:
            value = None

        if expected_type == bool:
            return bool(value)
        elif expected_type == int:
            return int(value) if value is not None else None
        elif expected_type == float:
            return float(value) if value is not None else None
        elif expected_type == str:
            return str(value)
        return value
