from datetime import datetime

from features.tasks import get_tasks
from pages import factory
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from device.dg4202 import DG4202
from scheduler.timekeeper import Timekeeper


class SchedulerWidget(QWidget):
    def __init__(self, timekeeper: Timekeeper = None):
        super().__init__()
        self.task_names = [func[0] for func in get_tasks()]
        self.timekeeper = timekeeper or factory.timekeeper
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # DateTime picker for scheduling tasks
        self.dateTimeEdit = QDateTimeEdit(self)
        self.dateTimeEdit.setDateTime(datetime.now())
        layout.addWidget(self.dateTimeEdit)

        # Label and list for displaying current jobs
        self.jobsLabel = QLabel("Current Jobs:", self)
        layout.addWidget(self.jobsLabel)
        self.jobsList = QListWidget(self)
        self.update_jobs_list()
        layout.addWidget(self.jobsList)

        # Button to configure a job
        self.configureJobButton = QPushButton("Schedule Task", self)
        self.configureJobButton.clicked.connect(self.open_job_config_popup)
        layout.addWidget(self.configureJobButton)

    def schedule_task(self):
        pass

    def update_jobs_list(self):
        # Update the list of jobs
        self.jobsList.clear()
        jobs = self.timekeeper.get_jobs()
        for job_id, job_info in jobs.items():
            self.jobsList.addItem(
                f"Job ID: {job_id}, Task: {job_info['task']}, Scheduled: {job_info['schedule_time']}"
            )

    def open_job_config_popup(self):
        # Open a popup window to configure a new job
        self.popup = JobConfigPopup()
        self.popup.exec()


class JobConfigPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.deviceSelect = QComboBox(self)
        self.deviceSelect.addItems(factory.DEVICE_LIST)
        self.deviceSelect.currentIndexChanged.connect(self.updateUI)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Device selection dropdown
        self.layout.addWidget(self.deviceSelect)

        # Placeholder for device-specific UI elements
        self.deviceSpecificLayout = QVBoxLayout()
        self.layout.addLayout(self.deviceSpecificLayout)

        self.updateUI()  # Initial UI update based on the default device selection

        # OK and Cancel buttons
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        self.layout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(self.cancelButton)

    def updateUI(self):
        # Clear existing device-specific UI elements
        while self.deviceSpecificLayout.count():
            child = self.deviceSpecificLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Update UI based on selected device
        selected_device = self.deviceSelect.currentText()
        if selected_device == "DG4202":
            self.configureDG4202Parameters()
        elif selected_device == "EDUX1002A":
            self.configureEDUX1002AParameters()
        # Add cases for other devices as needed

    def configureDG4202Parameters(self):
        # Channel input
        self.channelInput = QLineEdit(self)
        self.deviceSpecificLayout.addWidget(QLabel("Channel:"))
        self.deviceSpecificLayout.addWidget(self.channelInput)

        # Waveform type dropdown
        self.waveformTypeInput = QComboBox(self)
        self.waveformTypeInput.addItems(DG4202.available_waveforms())
        self.deviceSpecificLayout.addWidget(QLabel("Waveform Type:"))
        self.deviceSpecificLayout.addWidget(self.waveformTypeInput)

        # Frequency input
        self.frequencyInput = QLineEdit(self)
        self.deviceSpecificLayout.addWidget(QLabel("Frequency (Hz):"))
        self.deviceSpecificLayout.addWidget(self.frequencyInput)

        # Amplitude input
        self.amplitudeInput = QLineEdit(self)
        self.deviceSpecificLayout.addWidget(QLabel("Amplitude:"))
        self.deviceSpecificLayout.addWidget(self.amplitudeInput)

        # Offset input
        self.offsetInput = QLineEdit(self)
        self.deviceSpecificLayout.addWidget(QLabel("Offset:"))
        self.deviceSpecificLayout.addWidget(self.offsetInput)

    def configureEDUX1002AParameters(self):
        self.channelInput = QLineEdit(self)
        self.deviceSpecificLayout.addWidget(self.channelInput)

    def accept(self):
        selected_device = self.deviceSelect.currentText()
        if selected_device == "DG4202":
            params = self.getDG4202Parameters()
            task_name = (
                "task_set_waveform_parameters"  # Replace with the actual task name
            )
            schedule_time = self.dateTimeEdit.dateTime().toPyDateTime()

            # Schedule the task
            self.timekeeper.add_job(task_name, schedule_time, **params)
        elif selected_device == "EDUX1002A":
            # Handling for EDUX1002A
            pass

        super().accept()

    def getDG4202Parameters(self):
        # Retrieve values from UI elements
        channel = int(self.channelInput.text())
        waveform_type = self.waveformTypeInput.currentText()
        frequency = float(self.frequencyInput.text())
        amplitude = float(self.amplitudeInput.text())
        offset = float(self.offsetInput.text())

        # Construct the parameter dictionary
        params = {
            "channel": channel,
            "waveform_type": waveform_type,
            "frequency": frequency,
            "amplitude": amplitude,
            "offset": offset,
        }
        return params

    def getEDUX1002AParameters(self):
        pass
        # Retrieve and return parameters for EDUX1002A
        # ... Define the logic to get parameters for EDUX1002A


# Rest of the application code remains the same


if __name__ == "__main__":
    import sys

    # === FOR DEBUGGING=== #
    from scheduler.worker import Worker

    factory.worker = Worker(
        function_map_file=factory.FUNCTION_MAP_FILE,
        logfile=factory.WORKER_LOGS,
    )
    factory.timekeeper = Timekeeper(
        persistence_file=factory.TIMEKEEPER_JOBS_FILE,
        worker_instance=factory.worker,
        logfile=factory.TIMEKEEPER_LOGS,
    )
    for task_name, func_pointer in get_tasks():
        factory.worker.register_task(func_pointer, task_name)
    # === FOR DEBUGGING=== #

    app_qt = QApplication(sys.argv)
    ex = SchedulerWidget(timekeeper=factory.timekeeper)
    ex.show()
    sys.exit(app_qt.exec())
