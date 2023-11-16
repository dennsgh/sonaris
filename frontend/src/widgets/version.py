
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QMessageBox


class VersionWindow(QMessageBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Version Information")
        self.setText("MRILabs\nVersion: 1.0.0")  # Example version text
        self.setIcon(QMessageBox.Icon.Information)