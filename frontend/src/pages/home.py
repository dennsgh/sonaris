from PyQt6.QtWidgets import QLabel, QVBoxLayout
from pages.templates import BasePage


class HomePage(BasePage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Welcome")
        markdown = QLabel("Currently under development, check in later!")
        layout.addWidget(label)
        layout.addWidget(markdown)
        self.setLayout(layout)
