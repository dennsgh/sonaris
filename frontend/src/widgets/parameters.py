import ast

from features.tasks import TASK_USER_INTERFACE_DICTIONARY, get_tasks
from PyQt6.QtWidgets import QComboBox, QLabel, QLineEdit, QVBoxLayout, QWidget


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
        if component["type"] == "QComboBox":
            comboBox = QComboBox(self)
            options = component.get("options", [])
            if "options_function" in component:
                options = ast.literal_eval(component["options_function"])()
            comboBox.addItems(options)
            default = component.get("default")
            if default and default in options:
                comboBox.setCurrentIndex(options.index(default))
            self.layout.addWidget(QLabel(component["label"]))
            self.layout.addWidget(comboBox)
        elif component["type"] == "QLineEdit":
            lineEdit = QLineEdit(self)
            default = component.get("default", "")
            lineEdit.setText(str(default))
            self.layout.addWidget(QLabel(component["label"]))
            self.layout.addWidget(lineEdit)

    def getParameters(self):
        # Implement logic to collect parameters from the UI elements
        pass
