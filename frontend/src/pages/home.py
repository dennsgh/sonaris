from PyQt6.QtWidgets import QLabel, QVBoxLayout
from pages.templates import BasePage


class HomePage(BasePage):

    def __init__(self, parent=None, args_dict: dict = None):
        super().__init__(parent=parent)
        self.args_dict = args_dict
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Welcome")
        markdown = QLabel("""
                          Version 0.1.0
                          """)
        layout.addWidget(label)
        layout.addWidget(markdown)
        self.setLayout(layout)
