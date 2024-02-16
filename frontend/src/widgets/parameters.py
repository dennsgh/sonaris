from PyQt6.QtWidgets import QComboBox, QLabel, QLineEdit, QVBoxLayout, QWidget


class ParameterConfiguration(QWidget):
    def __init__(self, task_dictionary, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.task_dictionary = task_dictionary
        self.widget_cache = {}  # Adjusted to cache widgets explicitly

    def updateUI(self, device, task_name):
        if (device, task_name) in self.widget_cache:
            print(f"Showing {device} - {task_name}")
            self.show_cached_ui(device, task_name)
        else:
            print(f"Creating {device} - {task_name}")
            spec = self.task_dictionary.get(device, {}).get(task_name, [])
            self.clear_ui()  # Ensure the UI is clear before generating new widgets
            widgets = self.generateUI(spec)
            self.widget_cache[f"({device}, {task_name})"] = widgets

    def generateUI(self, spec):
        widgets = []  # Store created widgets in a list
        for component in spec:
            widget = self.createComponent(component)
            if widget:  # Check if widget is not None
                widgets.append(widget)  # Append the created widget to the list
                self.layout.addWidget(widget)  # Add widget to the layout
        return widgets  # Return the list of created widgets

    def show_cached_ui(self, device, task_name):
        self.clear_ui()  # Clear the layout before showing cached UI
        cached_widgets = self.widget_cache.get(f"({device},{task_name})", [])
        for widget in cached_widgets:
            if widget:  # Check if widget is not None
                self.main_layout.addWidget(widget)
                widget.setVisible(True)  # Ensure the widget is visible

    def clear_ui(self):
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(False)

    def get_parameters(self, task_spec):
        parameters = {}
        for spec in task_spec:
            kwarg_label = spec.get("kwarg_label", spec.get("label"))
            # Iterate through the layout to find the widget corresponding to the kwarg_label
            for i in range(self.main_layout.count()):
                widget = self.main_layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() == spec["label"]:
                    input_widget = self.main_layout.itemAt(i + 1).widget()
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
            return str(value)
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
            comboBox.addItems(options)
            if "default" in component:
                default_index = (
                    options.index(component["default"])
                    if component["default"] in options
                    else 0
                )
                comboBox.setCurrentIndex(default_index)
            self.main_layout.addWidget(QLabel(component["label"]))
            self.main_layout.addWidget(comboBox)
        # Handling for QLineEdit
        elif component["type"] == "QLineEdit":
            lineEdit = QLineEdit(self)
            if "default" in component:
                lineEdit.setText(str(component["default"]))
            self.main_layout.addWidget(QLabel(component["label"]))
            self.main_layout.addWidget(lineEdit)
        # Additional component types can be added here
