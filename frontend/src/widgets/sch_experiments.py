from enum import Enum
import inspect
import yaml
from features.task_validator import validate_configuration, get_function_to_validate, get_task_enum_name,get_task_enum_value, is_in_enum
from PyQt6.QtWidgets import (
    QCheckBox,
    QScrollArea,
    QFormLayout,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ExperimentConfiguration(QWidget):
    def __init__(self, parent=None, task_functions: dict = None, task_enum: Enum = None):
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
        self.descriptionWidget.setText("Load an experiment configuration to see its details here.")
        self.main_layout.addWidget(self.descriptionWidget)

    def addValidation(self, lineEdit):
        lineEdit.textChanged.connect(self.validateInput)

    def validateInput(self, text):
        if not text.strip():
            self.setStyleSheet("QLineEdit { border: 1px solid red; }")
        else:
            self.setStyleSheet("QLineEdit { border: none; }")

    def loadConfiguration(self, config_path):
        try:
            with open(config_path, "r") as file:
                self.config = yaml.safe_load(file)
            valid, message = self.validate_and_display()
            self.displayExperimentDetails()
            self.update() 
            return True, "Configuration loaded successfully."
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load or parse the configuration: {str(e)}")
            self.descriptionWidget.setText("Failed to load or parse the configuration.")
            return False, "Failed to load or parse the configuration."

    def validate_and_display(self):
        if not self.config:
            QMessageBox.warning(self, "Error", "No configuration loaded.")
            return
        
        validation_results = validate_configuration(self.config, self.task_functions, self.task_enum)
        
        overall_valid = True
        messages = []

        for task_name, is_valid, message in validation_results:
            if not is_valid:
                overall_valid = False
                messages.append(f"{task_name}: {message}")
        
        if not overall_valid:
            QMessageBox.warning(self, "Configuration Validation Failed", "\n".join(messages))
            self.descriptionWidget.setText("Configuration validation failed:\n" + "\n".join(messages))
        else:
            self.displayExperimentDetails()

        return overall_valid, "\n".join(messages)

    def displayExperimentDetails(self):
        if not self.config:
            QMessageBox.warning(self, "Error", "No configuration loaded.")
            return

        self.tabWidget.clear()
        steps = self.config.get('experiment', {}).get('steps', [])
        if steps:
            for step in steps:
                self.createTaskTab(step)

    def get_function(self,task):
        return get_function_to_validate(task,self.task_functions,self.task_enum)
    
    def createTaskTab(self, task:dict):
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
        # Inspect the function to get parameter types
        sig = inspect.signature(task_function)
        param_types = {name: param.annotation for name, param in sig.parameters.items()}

        for param, value in task.get("parameters", [{}])[0].items():
            expected_type = param_types.get(param, str)  # Default to str if type not found
            widget = self.createWidgetForParam(param, value, expected_type)
            # Create a label for the parameter name, which will be used for matching in getConfiguration
            paramNameLabel = QLabel(f"{param}")
            # Optionally, create another label for type hinting, not used in matching
            typeHintLabel = QLabel(f"Type: {expected_type.__name__}")
            # Add both the parameter name label and the widget to the form layout
            formLayout.addRow(paramNameLabel, widget)
            # Optionally, add the type hint label to the layout, perhaps in a different column or as a tooltip
            widget.setToolTip(f"Expected Type: {expected_type.__name__}")

        scrollArea.setWidget(formWidget)
        self.tabWidget.addTab(tab, get_task_enum_value(task.get("task"),self.task_enum))

    def createWidgetForParam(self, param, value, expected_type):
        # Only create a QCheckBox for boolean values
        if isinstance(value, bool):
            checkBox = QCheckBox()
            checkBox.setChecked(value)
            return checkBox
        else:
            # Use QLineEdit for all other data types
            lineEdit = QLineEdit()
            # Convert the value to a string for display
            lineEdit.setText(str(value))
            self.addValidation(lineEdit)  # Optionally add validation
            return lineEdit


    def getConfiguration(self):
        """
        Collects the configuration from the UI, reflecting any changes made by the user,
        while strictly preserving the original data structure and types.
        """
        # Start with the base structure of the experiment configuration.
        updated_config = {
            'experiment': {
                'name': self.config.get('experiment', {}).get('name', 'Unnamed Experiment'),
                'steps': []
            }
        }

        # Iterate over each tab, which corresponds to a step in the experiment.
        for index in range(self.tabWidget.count()):
            step_widget = self.tabWidget.widget(index)
            original_step = self.config['experiment']['steps'][index]
            print(original_step)
            # Copy the step structure from the original to maintain any keys and their order.
            updated_step = original_step.copy()

            # Assuming parameters are stored in a QScrollArea -> QWidget -> QFormLayout in the tab.
            scroll_area = step_widget.findChild(QScrollArea)
            form_widget = scroll_area.widget()
            form_layout = form_widget.layout()

            updated_parameters = []
            for param_group in original_step['parameters']:
                updated_param_group = {}
                for param, value in param_group.items():
                    # Find the widget corresponding to this parameter.
                    for i in range(form_layout.rowCount()):
                        label_widget = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
                        if label_widget.text() == param:
                            input_widget = form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
                            updated_value = self.getValueFromWidget(input_widget, type(value))
                            updated_param_group[param] = updated_value
                            break
                updated_parameters.append(updated_param_group)

            updated_step['parameters'] = updated_parameters
            updated_config['experiment']['steps'].append(updated_step)

        return updated_config

    def getValueFromWidget(self, widget, value_type):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QLineEdit):
            text = widget.text()
            # Try to convert text to the expected value type
            try:
                if value_type == bool:
                    # Consider specific logic for converting text to bool if necessary
                    return text.lower() in ['true', '1', 't', 'y', 'yes']
                elif value_type == int:
                    return int(text)
                elif value_type == float:
                    return float(text)
                else:
                    return text  # Return as string by default
            except ValueError:
                # Handle or log the error as appropriate
                print(f"Error converting '{text}' to {value_type}")
                return None
        else:
            # Handle other widget types as needed
            return None


    def saveConfiguration(self, config_path):
        """
        Saves the currently displayed configuration back to a file.
        """
        config = self.getConfiguration()
        try:
            with open(config_path, 'w') as file:
                yaml.dump(config, file, sort_keys=False)
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")