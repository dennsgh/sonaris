import inspect
from enum import Enum

import yaml
from features.task_validator import (
    get_function_to_validate,
    get_task_enum_value,
    validate_configuration,
)
from header import ErrorLevel
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
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
        valid, message, descriptionText = self.load_and_display(config_path)
        self.descriptionWidget.setText(descriptionText)

        if valid:
            self.displayExperimentDetails()
            self.update()
            return True, "Configuration loaded successfully."
        else:
            return False, "Failed to load or parse the configuration."

    def validate(self, data: dict):
        overall_valid = True
        highest_error_level = ErrorLevel.INFO  # Assume the lowest severity to start
        validation_results = validate_configuration(
            data, self.task_functions, self.task_enum
        )
        messages = (
            []
        )  # This will accumulate our error messages in a more compact format

        for task_name, is_valid, message, error_level in validation_results:
            if not is_valid:
                overall_valid = False
                # Update the highest error level based on the current error
                if error_level.value > highest_error_level.value:
                    highest_error_level = error_level
            # Append the task and its message in a compact manner
            messages.append(f"{task_name}: {message}")

        # Join messages with a separator that puts each on a new line but in a more compact form
        compact_message = "\n".join(messages)

        return overall_valid, compact_message, highest_error_level

    def error_handling(self, overall_valid, messages, highest_error_level):
        if overall_valid or highest_error_level == ErrorLevel.INFO:
            descriptionText = self.generate_experiment_summary(self.config)
        else:
            descriptionText = (
                "OK"  # Default message, will be overwritten by error cases below
            )

        # Handle different levels of error messages
        if highest_error_level == ErrorLevel.BAD_CONFIG:
            QMessageBox.warning(
                self, "Configuration Validation Issues", "".join(messages)
            )
            descriptionText = "Configuration Validation Issues: " + "\n".join(messages)
        elif highest_error_level == ErrorLevel.INVALID_YAML:
            QMessageBox.critical(
                self, "Configuration Validation Failed", "".join(messages)
            )
            descriptionText = "Configuration Validation Failed: " + "\n".join(messages)
        return descriptionText

    def load_and_display(self, config_path):
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)
        if not self.config:
            QMessageBox.warning(self, "Error", "No configuration loaded.")
            return

        overall_valid, messages, highest_error_level = self.validate(self.config)
        # Initialize description text with a default message or an experiment summary
        # Generate a summary if the config is valid or if only INFO level messages are present
        descriptionText = self.error_handling(
            overall_valid, messages, highest_error_level
        )
        return overall_valid, "\n".join(messages), descriptionText

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
        Creates a tab for each experiment step and handles its widgets and validation,
        iterating through the function's parameters for UI generation.
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

        # Initialize a dictionary to store the task parameters from the configuration
        task_parameters = task.get("parameters", {})

        for param_name, param in sig.parameters.items():
            # Retrieve the parameter value from the task configuration if available
            # Otherwise, set a default value or handle the missing case as appropriate
            value = task_parameters.get(
                param_name, None
            )  # Adjust the default value as needed

            expected_type = param_types.get(
                param_name, str
            )  # Default to str if not specified

            # Create appropriate widget based on expected type and enforce range limits
            param_constraints = getattr(task_function, "param_constraints", {})
            widget = UIComponentFactory.create_widget(
                param_name, value, expected_type, param_constraints
            )

            # Create labels for parameter name and type hinting (optional)
            paramNameLabel = QLabel(f"{param_name} :{expected_type.__name__}")
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
        overall_valid, messages, highest_error_level = self.validate(data)
        descriptionText = self.error_handling(
            overall_valid, messages, highest_error_level
        )
        if not overall_valid:
            self.descriptionWidget.setText(descriptionText)
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

    def generate_experiment_summary(self, data: dict):
        """
        Generates a summary of the experiment based on the YAML configuration.
        This is a placeholder function; you should replace the logic with actual
        processing of your specific YAML structure to extract and format the summary.
        """
        # Pseudocode for generating a summary - replace with actual implementation
        experiment_name = data.get("experiment_name", "Unnamed Experiment")
        parameters = data.get("parameters", {})
        objectives = data.get("objectives", [])

        summary_lines = [
            f"Experiment: {experiment_name}",
            "Parameters:",
        ]
        for param, value in parameters.items():
            summary_lines.append(f"  - {param}: {value}")

        summary_lines.append("Objectives:")
        for objective in objectives:
            summary_lines.append(f"  - {objective}")

        return "\n".join(summary_lines)

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
