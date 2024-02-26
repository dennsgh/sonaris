import inspect
from enum import Enum

import yaml
from features.task_validator import (
    get_function_to_validate,
    get_task_enum_value,
    validate_configuration,
)
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from widgets.ui_factory import UIComponentFactory


class ExperimentConfiguration(QWidget):
    def __init__(
        self, parent=None, task_functions: dict = None, task_enum: Enum = None
    ):
        super().__init__(parent)
        self.task_functions = task_functions
        self.task_enum = task_enum
        self.config = None
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        self.main_layout.addWidget(self.tabWidget)
        self.descriptionWidget = QTextEdit(self)
        self.descriptionWidget.setReadOnly(True)
        self.descriptionWidget.setText(
            "Load an experiment configuration to see its details here."
        )
        self.main_layout.addWidget(self.descriptionWidget)

    def loadConfiguration(self, config_path):
        try:
            with open(config_path, "r") as file:
                self.config = yaml.safe_load(file)
            valid, message = self.validate_and_display()
            self.displayExperimentDetails()
            self.update()
            return True, "Configuration loaded successfully."
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load or parse the configuration: {str(e)}"
            )
            self.descriptionWidget.setText("Failed to load or parse the configuration.")
            return False, "Failed to load or parse the configuration."

    def validate(self, data: dict):
        overall_valid = True
        validation_results = validate_configuration(
            data, self.task_functions, self.task_enum
        )
        messages = []
        for task_name, is_valid, message in validation_results:
            if not is_valid:
                overall_valid = False
                messages.append(f"{task_name}: {message}")

        return overall_valid, "\n".join(messages)

    def validate_and_display(self):
        if not self.config:
            QMessageBox.warning(self, "Error", "No configuration loaded.")
            return
        overall_valid, messages = self.validate(self.config)

        if not overall_valid:
            QMessageBox.warning(
                self, "Configuration Validation Failed", "\n".join(messages)
            )
            self.descriptionWidget.setText(
                "Configuration validation failed:\n" + "\n".join(messages)
            )
        else:
            self.displayExperimentDetails()

        return overall_valid, "\n".join(messages)

    def displayExperimentDetails(self):
        if not self.config:
            QMessageBox.warning(self, "Error", "No configuration loaded.")
            return

        self.tabWidget.clear()
        steps = self.config.get("experiment", {}).get("steps", [])
        if steps:
            for step in steps:
                self.createTaskTab(step)

    def get_function(self, task):
        return get_function_to_validate(task, self.task_functions, self.task_enum)

    def createTaskTab(self, task: dict):
        """
        Creates a tab for each experiment step and handles its widgets and validation.
        """

        tab = QWidget()
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        layout = QVBoxLayout(tab)
        layout.addWidget(scrollArea)
        formWidget = QWidget()
        formLayout = QFormLayout()
        formWidget.setLayout(formLayout)

        task_function = self.get_function(task.get("task"))

        if not task_function:
            print(f"No function found for task: {task}")
            return

        # Inspect the function signature to get parameter information
        sig = inspect.signature(task_function)
        param_types = {name: param.annotation for name, param in sig.parameters.items()}

        for param, value in task.get("parameters", {}).items():
            expected_type = param_types.get(param, str)  # Default to str if not found

            # Create appropriate widget based on expected type and enforce range limits
            param_constraints = getattr(task_function, "param_constraints", {})
            widget = UIComponentFactory.create_widget(
                param, value, expected_type, param_constraints
            )

            # Create labels for parameter name and type hinting (optional)
            paramNameLabel = QLabel(f"{param} :{expected_type.__name__}")
            # Add labels and widget to the form layout
            formLayout.addRow(paramNameLabel, widget)

        scrollArea.setWidget(formWidget)
        self.tabWidget.addTab(
            tab, get_task_enum_value(task.get("task"), self.task_enum)
        )

    def getUserData(self):
        """
        Collects the configuration from the UI, validating input and preserving data types.
        """
        updated_config = {
            "experiment": {
                "name": self.config.get("experiment", {}).get(
                    "name", "Unnamed Experiment"
                ),
                "steps": [],
            }
        }

        for index in range(self.tabWidget.count()):
            step_widget = self.tabWidget.widget(index)
            original_step = self.config["experiment"]["steps"][index]

            updated_step = original_step.copy()
            updated_parameters = {}

            # Extract the QWidget that holds the form layout for the current step
            form_widget = step_widget.findChild(QScrollArea).widget()
            form_layout = form_widget.layout()

            # Reconstruct the parameters from UI components
            for i in range(form_layout.rowCount()):
                row_widget = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                if row_widget:
                    param_label_widget = row_widget.widget()
                    param_name = param_label_widget.text().split(" :")[
                        0
                    ]  # Extract parameter name before the colon
                    input_widget = form_layout.itemAt(
                        i, QFormLayout.ItemRole.FieldRole
                    ).widget()
                    param_value = UIComponentFactory.extract_value(input_widget)
                    if param_value is None:  # None indicates it wasn't recognized.
                        continue

                    updated_parameters[param_name] = param_value

            updated_step["parameters"] = updated_parameters
            updated_config["experiment"]["steps"].append(updated_step)

        return updated_config

    def getConfiguration(self):
        """
        Collects the validated configuration from the UI and prepares it for use or saving.
        """
        # Extract the user-modified configuration from the UI elements
        data = self.getUserData()

        # Validate the extracted data
        valid, message = self.validate(data)
        if not valid:
            QMessageBox.critical(self, "Validation Error", message)
            raise ValueError("Configuration validation failed.")

        return data

    def validate_and_convert_value(self, text, expected_type):
        """
        Validates and converts text input to the expected data type.
        Raises ValueError if the value is invalid.
        """

        if expected_type == bool:
            # Specific logic for converting text to bool
            return text.lower() in ["true", "1", "t", "y", "yes", "ok", "on"]
        elif expected_type in (int, float):
            if expected_type == int:
                return int(text)
            else:
                return float(text)
        else:
            return text  # Return as string by default

    def saveConfiguration(self, config_path):
        """
        Saves the configuration to a file, handling potential errors.
        """

        config = self.getConfiguration()
        try:
            with open(config_path, "w") as file:
                yaml.dump(config, file, sort_keys=False)
            QMessageBox.information(
                self, "Success", "Configuration saved successfully."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to save configuration: {str(e)}"
            )


# Helper function to retrieve the type information from a widget
def get_type_from_widget(widget):
    """
    Extracts the property type information from the widget's meta-object.
    """

    meta_object = widget.metaObject()
    for i in range(meta_object.propertyCount()):
        prop = meta_object.property(i)
        if prop.name() == b"expectedType":
            return prop.type()
    return None
