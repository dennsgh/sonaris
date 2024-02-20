import yaml
from features.tasks import TASK_LIST_DICTIONARY, TaskName
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
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


class ExperimentConfiguration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.config = None  # Hold the loaded YAML config
        self.experimentDescriptionWidget = QTextEdit(self)
        self.experimentDescriptionWidget.setReadOnly(True)
        self.parameters = {}
        self.initUI()

    def initUI(self):
        # Initial setup, possibly with a placeholder text
        self.experimentDescriptionWidget.setText(
            "Load an experiment configuration to see its details here."
        )
        self.main_layout.addWidget(self.experimentDescriptionWidget)
        # Add a table to display the parameters
        self.parametersTable = QTableWidget(self)
        self.parametersTable.setColumnCount(2)  # For parameter name and value
        self.parametersTable.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.parametersTable.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # Make the table read-only in PyQt6

        self.main_layout.addWidget(self.parametersTable)
        self.main_layout.addWidget(self.experimentDescriptionWidget)

    def get_experiment(self):
        # Assuming the experiment is defined at the root of the YAML file
        return self.config.get("experiment", {})

    def get_experiment_steps(self):
        experiment = self.get_experiment()
        return experiment.get("steps", [])

    def updateUI(self, parameters):
        container = QWidget()
        layout = QVBoxLayout(container)

        for param in parameters:
            if param["type"] == "QComboBox":
                comboBox = QComboBox(container)
                options = param.get("options", [])
                comboBox.addItems(options)
                layout.addWidget(QLabel(param["label"], container))
                layout.addWidget(comboBox)
            elif param["type"] == "QLineEdit":
                lineEdit = QLineEdit(container)
                layout.addWidget(QLabel(param["label"], container))
                layout.addWidget(lineEdit)

        container.setLayout(layout)
        return container

    def loadConfiguration(self, config_path):
        """Loads and parses the YAML configuration file."""
        try:
            with open(config_path, "r") as file:
                self.config = yaml.safe_load(file)

            valid, message = self.validate_configuration()
            if not valid:
                QMessageBox.warning(self, "Configuration Validation Failed", message)
                self.experimentDescriptionWidget.setText(
                    "Configuration validation failed:\n" + message
                )
                return

            self.displayExperimentDetails()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load or parse the configuration: {str(e)}"
            )
            self.experimentDescriptionWidget.setText(
                "Failed to load or parse the configuration."
            )

    def displayExperimentDetails(self):
        """Updates the UI to display details about the loaded experiment."""
        if not self.config:
            self.experimentDescriptionWidget.setText(
                "Failed to load or parse the configuration."
            )
            return

        self.populateParametersTable()

    def populateParametersTable(self):
        steps = self.get_experiment_steps()
        self.parametersTable.setRowCount(0)  # Clear the table first

        for step in steps:
            for parameter in step.get("parameters", []):
                for param, value in parameter.items():
                    row_position = self.parametersTable.rowCount()
                    self.parametersTable.insertRow(row_position)
                    self.parametersTable.setItem(
                        row_position, 0, QTableWidgetItem(str(param))
                    )
                    self.parametersTable.setItem(
                        row_position, 1, QTableWidgetItem(str(value))
                    )

        self.parametersTable.resizeColumnsToContents()

        # Assuming the experiment details are to be presented in a human-readable format
        details = "Experiment Overview:\n"
        experiment = self.config.get("experiment", {})
        steps = experiment.get("steps", [])

        for i, step in enumerate(steps, start=1):
            details += (
                f"\nStep {i}: {step.get('description', 'No description provided.')}"
            )
            # Parameters are a list of dictionaries; iterate accordingly
            for parameter in step.get(
                "parameters", []
            ):  # Now it correctly handles a list
                for param, value in parameter.items():  # parameter is a dictionary
                    details += f"\n - {param}: {value}"

        self.experimentDescriptionWidget.setText(details)

    def validate_configuration(self):
        if not self.config:
            return False, "No configuration loaded."

        valid = True
        error_messages = []

        steps = self.get_experiment_steps()
        for step in steps:
            task_name_str = step.get("task")
            task_name_enum = TaskName.get_task_name_enum(task_name_str)
            if task_name_enum is None:
                valid = False
                error_messages.append(
                    f"Task '{task_name_str}' does not match any TaskName enum."
                )
                continue

            # Now, find which device supports this task
            task_supported = False
            for device, tasks in TASK_LIST_DICTIONARY.items():
                if task_name_enum.value in tasks:
                    task_supported = True
                    # Further validation for parameters can be performed here
                    break

            if not task_supported:
                valid = False
                error_messages.append(
                    f"Task '{task_name_str}' is not supported by any device."
                )

        return valid, "\n".join(error_messages)
