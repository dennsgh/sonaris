from features.tasks import TASK_USER_INTERFACE_DICTIONARY
from PyQt6.QtWidgets import QComboBox, QLabel, QLineEdit, QVBoxLayout, QWidget

from device.dg4202 import DG4202  # will be dynamically imported later


class ParameterConfiguration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.widget_cache = {}  # Cache for storing widgets

    def updateUI(self, device, task_name):
        # Check if the task's UI is already in the cache
        if (device, task_name) in self.widget_cache:
            self.show_cached_ui(device, task_name)
            return

        spec = TASK_USER_INTERFACE_DICTIONARY.get(device, {}).get(task_name, [])
        self.generateUI(spec)
        # Cache the newly created UI
        self.widget_cache[(device, task_name)] = self.layout.children()

    def generateUI(self, spec):
        # Clear existing UI elements
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create UI elements based on the spec
        for component in spec:
            self.createComponent(component)

    def show_cached_ui(self, device, task_name):
        # Clear existing UI elements
        self.clear_ui()
        # Add cached widgets to the layout
        for widget in self.widget_cache[(device, task_name)]:
            self.layout.addWidget(widget)

    def clear_ui(self):
        # Clear existing UI elements
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def get_parameters(self, task_spec):
        parameters = {}
        for spec in task_spec:
            kwarg_label = spec.get("kwarg_label", spec.get("label"))
            # Iterate through the layout to find the widget corresponding to the kwarg_label
            for i in range(self.layout.count()):
                widget = self.layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() == spec["label"]:
                    input_widget = self.layout.itemAt(i + 1).widget()
                    value = self.extract_value(input_widget, spec)
                    parameters[kwarg_label] = value
                    break
        return parameters

    def extract_value(self, widget, spec):
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
            return value
        elif spec.get("data_type") == "bool":
            # Assuming that boolean values are represented by specific strings (e.g., "ON" or "OFF")
            return value.lower() in ["on", "true", "1"]
        else:
            return value

    def createComponent(self, component):
        # Handling for QComboBox
        if component["type"] == "QComboBox":
            comboBox = QComboBox(self)
            options = component.get("options", [])
            if "options_function" in component:
                options = eval(component["options_function"])()  # Use eval carefully
            comboBox.addItems(options)
            if "default" in component:
                default_index = (
                    options.index(component["default"])
                    if component["default"] in options
                    else 0
                )
                comboBox.setCurrentIndex(default_index)
            self.layout.addWidget(QLabel(component["label"]))
            self.layout.addWidget(comboBox)
        # Handling for QLineEdit
        elif component["type"] == "QLineEdit":
            lineEdit = QLineEdit(self)
            if "default" in component:
                lineEdit.setText(str(component["default"]))
            self.layout.addWidget(QLabel(component["label"]))
            self.layout.addWidget(lineEdit)
        # Additional component types can be added here
