from PyQt6.QtWidgets import QListWidget
from PyQt6.QtCore import pyqtSignal


class Sidebar(QListWidget):

    # Define a custom signal that will send the selected page name (str) when an item is clicked
    pageSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(200)

        # Connect the built-in itemClicked signal to our custom slot
        self.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item):
        # Emit our custom signal with the page name
        self.pageSelected.emit(item.text())
