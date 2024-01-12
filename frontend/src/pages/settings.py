import json
import os
from pathlib import Path
from typing import Callable

from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout
from widgets.templates import BasePage


class SettingsPage(BasePage):
    def __init__(
        self,
        parent=None,
        args_dict: dict = None,
        root_callback: Callable = None,
    ):
        super().__init__(
            parent=parent, args_dict=args_dict, root_callback=root_callback
        )
        self.args_dict = args_dict
        self.settings_file = Path(os.getenv("DATA"), "settings.json")
        self.load_settings()
        self.initUI()
        self.setLayout(self.main_layout)

    def update(self):
        pass

    def initUI(self):
        self.main_layout = QVBoxLayout()

        # Add a label and edit for a sample setting
        self.setting_label = QLabel("Sample Setting:")
        self.setting_edit = QLineEdit(self)
        self.setting_edit.setText(self.settings.get("sample_setting", ""))

        # Create buttons
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_settings)

        # Arrange widgets in the layout
        self.main_layout.addWidget(self.setting_label)
        self.main_layout.addWidget(self.setting_edit)
        self.main_layout.addWidget(self.apply_button)
        self.main_layout.addWidget(self.reset_button)

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {}

    def save_settings(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def apply_settings(self):
        # Save the current state of the settings
        self.settings["sample_setting"] = self.setting_edit.text()
        self.save_settings()

    def reset_settings(self):
        # Reset the settings to their saved state
        self.load_settings()
        self.setting_edit.setText(self.settings.get("sample_setting", ""))


# To use this dialog:
# if __name__ == "__main__":
#     import sys
#     app = QApplication(sys.argv)
#     settings_page = SettingsPage()
#     settings_page.exec()
