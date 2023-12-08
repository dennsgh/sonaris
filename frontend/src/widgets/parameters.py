import ast

from features.tasks import TASK_USER_INTERFACE_DICTIONARY
from PyQt6.QtWidgets import QComboBox, QLabel, QLineEdit, QVBoxLayout, QWidget

from device.dg4202 import DG4202  # will be dynamically imported later


class ParameterConfiguration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

    def updateUI(self, device, task_name):
        spec = TASK_USER_INTERFACE_DICTIONARY.get(device, {}).get(task_name, [])
        self.generateUI(spec)

    def generateUI(self, spec):
        # Clear existing UI elements
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Create UI elements based on the spec
        for component in spec:
            self.createComponent(component)

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

    def getParameters(self):
        # Logic to collect parameters from the UI elements
        # Implement as needed
        pass
