from datetime import datetime, timedelta

from features.tasks import get_tasks
from pages import factory
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from widgets.parameters import ParameterConfiguration

from device.dg4202 import DG4202
from scheduler.timekeeper import Timekeeper


class SchedulerWidget(QWidget):
    def __init__(self, timekeeper: Timekeeper = None):
        super().__init__()
        # update to unpack getting ALL task names regardless of device for the widget, since it only looks at jobs.json
        self.task_names = [func[0] for func in get_tasks()]
        self.timekeeper = timekeeper or factory.timekeeper
        self.popup = JobConfigPopup(self.timekeeper)
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
        self.popup.exec()


class JobConfigPopup(QDialog):
    def __init__(self, timekeeper: Timekeeper):
        super().__init__()
        self.timekeeper = timekeeper
        self.deviceSelect = QComboBox(self)
        self.taskSelect = QComboBox(self)
        self.deviceSelect.addItems(factory.DEVICE_LIST)
        self.deviceSelect.currentIndexChanged.connect(self.updateTaskList)
        self.taskSelect.currentIndexChanged.connect(self.updateParameterUI)
        self.parameterConfig = ParameterConfiguration(self)
        self.initUI()

    def initUI(self):
        # Main horizontal layout
        mainLayout = QHBoxLayout(self)

        # Left column for device selection, task selection and time configuration
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(QLabel("Select Device:"))
        leftLayout.addWidget(self.deviceSelect)
        leftLayout.addWidget(QLabel("Select Task:"))
        leftLayout.addWidget(self.taskSelect)
        self.setupTimeConfiguration(leftLayout)
        mainLayout.addLayout(leftLayout)

        # Right column for parameter configuration
        mainLayout.addWidget(self.parameterConfig)

        # OK and Cancel buttons
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        self.layout().addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        self.layout().addWidget(self.cancelButton)

    def updateTaskList(self):
        # Update the task list based on the selected device
        selected_device = self.deviceSelect.currentText()
        tasks = get_tasks().get(selected_device, {}).keys()
        self.taskSelect.clear()
        self.taskSelect.addItems(tasks)

    def updateUI(self):
        selected_device = self.deviceSelect.currentText()
        selected_task = self.taskSelect.currentText()
        self.parameterConfig.updateUI(selected_device, selected_task)

    def setupTimeConfiguration(self, layout):
        # Time configuration options
        self.timestampRadioButton = QRadioButton("Timestamp")
        self.durationRadioButton = QRadioButton("Duration")
        layout.addWidget(self.timestampRadioButton)
        layout.addWidget(self.durationRadioButton)

        # Connect radio button signals to a method to toggle input visibility
        self.timestampRadioButton.toggled.connect(self.toggleTimeInputs)
        self.durationRadioButton.toggled.connect(self.toggleTimeInputs)

        # Timestamp inputs (default: datetime.now())
        self.timestampInputs = self.createDateTimeInputs(datetime.now())
        for input in self.timestampInputs:
            layout.addWidget(input)

        # Duration inputs (default: 0s)
        self.durationInputs = self.createDateTimeInputs(timedelta(seconds=0))
        for input in self.durationInputs:
            layout.addWidget(input)
            input.setVisible(False)

        # Set default selection
        self.timestampRadioButton.setChecked(True)

    def createDateTimeInputs(self, default_value):
        # Create input fields for date-time or duration
        inputs = []
        fields = ["day", "month", "year", "hour", "minute", "second", "millisecond"]
        for field in fields:
            lineEdit = QLineEdit(self)
            lineEdit.setText(str(getattr(default_value, field, 0)))
            inputs.append(lineEdit)
        return inputs

    def toggleTimeInputs(self):
        # Toggle visibility of time input fields based on selected option
        isTimestamp = self.timestampRadioButton.isChecked()
        for input in self.timestampInputs:
            input.setVisible(isTimestamp)
        for input in self.durationInputs:
            input.setVisible(not isTimestamp)

    def configureDG4202WaveParameters(self):
        # Channel input
        self.channelInput = QComboBox(self)
        self.channelInput.addItems(["1", "2"])
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
        # Schedule the task with either timestamp or duration
        selected_device = self.deviceSelect.currentText()
        if self.timestampRadioButton.isChecked():
            schedule_time = self.getDateTimeFromInputs(self.timestampInputs)
        else:
            duration = self.getDateTimeFromInputs(self.durationInputs, duration=True)
            schedule_time = datetime.now() + duration

        if selected_device == DeviceName.DG4202.value:
            task_name = "task_set_waveform_parameters"
            params = self.getDG4202Parameters()
            self.timekeeper.add_job(task_name, schedule_time, **params)
        elif selected_device == DeviceName.EDUX1002A.value:
            # Handling for EDUX1002A
            pass

        super().accept()

    def getDateTimeFromInputs(self, inputs, duration=False):
        # Create a datetime or timedelta object from input fields
        values = [int(input.text()) for input in inputs]
        if duration:
            return timedelta(
                days=values[0],
                months=values[1],
                years=values[2],
                hours=values[3],
                minutes=values[4],
                seconds=values[5],
                milliseconds=values[6],
            )
        else:
            return datetime(
                day=values[0],
                month=values[1],
                year=values[2],
                hour=values[3],
                minute=values[4],
                second=values[5],
                microsecond=values[6] * 1000,
            )

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
