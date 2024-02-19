from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class ParameterConfiguration(QWidget):
    def __init__(self, task_dictionary, parent=None):
        super().__init__(parent)
        self.task_dictionary = task_dictionary
        self.widget_cache = {}  # Cache for configurations
        self.stacked_widget = QStackedWidget(self)  # Use QStackedWidget to manage UIs
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(
            self.stacked_widget
        )  # Add the stacked widget to the main layout

    def updateUI(self, device, task_name):
        cache_key = (device, task_name)
        if cache_key not in self.widget_cache:
            print(f"Creating {device} - {task_name}")
            spec = self.task_dictionary.get(device, {}).get(task_name, [])
            container_widget = self.generateUI(spec)
            self.widget_cache[cache_key] = container_widget
            self.stacked_widget.addWidget(
                container_widget
            )  # Add new configuration to stacked widget

        # Switch to the relevant configuration
        self.stacked_widget.setCurrentWidget(self.widget_cache[cache_key])

    def createComponent(self, component, layout):
        # Adjust this method to add widgets to the passed layout
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
            layout.addWidget(QLabel(component["label"]))  # Add to the passed layout
            layout.addWidget(comboBox)  # Add to the passed layout
        elif component["type"] == "QLineEdit":
            lineEdit = QLineEdit(self)
            if "default" in component:
                lineEdit.setText(str(component["default"]))
            layout.addWidget(QLabel(component["label"]))  # Add to the passed layout
            layout.addWidget(lineEdit)  # Add to the passed layout
        # Implement other component types as needed

    def generateUI(self, spec):
        container = QWidget()  # Container for this set of parameters
        layout = QVBoxLayout(container)

        for component in spec:
            self.createComponent(
                component, layout
            )  # Pass the layout to createComponent

        container.setLayout(layout)
        return container

    def get_parameters(self, task_spec):
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
                        value = self.extract_value(input_widget, spec)
                        if value is not None:  # Only add if extraction was successful
                            parameters[kwarg_label] = value
                    break  # Break after finding the widget to avoid unnecessary iterations

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
