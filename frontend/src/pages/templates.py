from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QTimer


class BasePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    def layout(self):
        raise NotImplementedError

    def register_callbacks(self):
        pass  # Implement any necessary signal-slot connections here
