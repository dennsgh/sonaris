from PyQt6.QtWidgets import QLabel, QVBoxLayout
from pages.templates import ModuleWidget


class SettingsPage(ModuleWidget):

    def __init__(self, parent=None, args_dict: dict = None):
        super().__init__(parent=parent)
        self.args_dict = args_dict
        self.initUI()
        self.setLayout(self.main_layout)

    def initUI(self):
        self.main_layout = QVBoxLayout()
        label = QLabel("Welcome")
        markdown = QLabel("""
                          Version 0.1.0
                          """)
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(markdown)
