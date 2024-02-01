import json
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QListWidget, QSplitter, QHBoxLayout
from PyQt6.QtCore import QTimer
from datetime import datetime
from pathlib import Path
import os

class DeviceMonitorWidget(QWidget):
    def __init__(self, device_managers, monitor_logs: Path = None, parent=None):
        super().__init__(parent)
        self.device_managers = device_managers  # Dictionary of device managers
        self.monitor_logs = monitor_logs or Path(os.getenv("LOGS"), "monitor.json")
        self.device_statuses = {device_name: None for device_name in self.device_managers.keys()}
        self.initUI()
        self.setup_refresh_timer()
        self.load_event_log()

    def initUI(self):
        self.splitter = QSplitter(self)
        self.leftWidget = QWidget()
        self.leftLayout = QVBoxLayout(self.leftWidget)
        self.status_labels = {}

        # Create status labels for each device
        for device_name in self.device_managers.keys():
            label = QLabel(f"{device_name} Status: Checking...")
            self.leftLayout.addWidget(label)
            self.status_labels[device_name] = label

        # Refresh Button
        self.refresh_button = QPushButton("Refresh Status")
        self.refresh_button.clicked.connect(self.update_device_statuses)
        self.leftLayout.addWidget(self.refresh_button)

        # Right Side Widget and Layout
        self.rightWidget = QWidget()
        self.rightLayout = QVBoxLayout(self.rightWidget)
        self.event_log_list = QListWidget()
        self.rightLayout.addWidget(self.event_log_list)

        self.splitter.addWidget(self.leftWidget)
        self.splitter.addWidget(self.rightWidget)
        self.splitter.setSizes([300, 300])

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.addWidget(self.splitter)

    def setup_refresh_timer(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_device_statuses)
        self.refresh_timer.start(1000)  # Refresh every 1 second

    def load_event_log(self):
        if self.monitor_logs.exists():
            with open(self.monitor_logs, 'r') as file:
                event_log = json.load(file)
            for event in event_log:
                self.event_log_list.addItem(f"[{event['timestamp']}] - {event['description']}")

    def log_event(self, description):
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "description": description
        }
        if not self.monitor_logs.exists():
            with open(self.monitor_logs, 'w') as file:
                json.dump([event], file, indent=4)
        else:
            with open(self.monitor_logs, 'r+') as file:
                event_log = json.load(file)
                event_log.append(event)
                file.seek(0)
                json.dump(event_log, file, indent=4)
        self.event_log_list.addItem(f"[{timestamp}] - {description}")

    def update_device_statuses(self):
        for device_name, manager in self.device_managers.items():
            self.update_device_status(device_name, manager)

    def update_device_status(self, device_name, manager):
        is_alive = manager.is_device_alive()
        if is_alive and self.device_statuses[device_name] != is_alive:
            self.log_event(f"{device_name} Connected")
        elif not is_alive and self.device_statuses[device_name] != is_alive:
            self.log_event(f"{device_name} Disconnected")
        
        self.device_statuses[device_name] = is_alive
        status = "Connected" if is_alive else "Disconnected"
        self.status_labels[device_name].setText(f"{device_name} Status: {status}")