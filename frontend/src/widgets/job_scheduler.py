from datetime import datetime, timedelta
from typing import Callable

from features.tasks import TASK_USER_INTERFACE_DICTIONARY, get_tasks
from header import DeviceName
from pages import factory
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from widgets.parameters import ParameterConfiguration

from scheduler.timekeeper import Timekeeper


class SchedulerWidget(QWidget):
    def __init__(self, timekeeper: Timekeeper = None):
        super().__init__()
        # update to unpack getting ALL task names regardless of device for the widget, since it only looks at jobs.json
        self.timekeeper = timekeeper or factory.timekeeper
        self.popup = JobConfigPopup(self.timekeeper, self.popup_callback)
        self.timekeeper.set_callback(self.popup_callback)
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
                f"Task: {job_info['task']} Scheduled: {job_info['schedule_time']} {job_info['kwargs']} Job ID: {job_id}, "
            )

    def open_job_config_popup(self):
        # Open a popup window to configure a new job
        self.popup.exec()

    def popup_callback(self):
        # callback for the task scheduler objects to update the list.
        self.update_jobs_list()


class JobConfigPopup(QDialog):
    def __init__(self, timekeeper: Timekeeper, _callback: Callable):
        super().__init__()
        self.resize(800, 640)
        self.parameterConfig = ParameterConfiguration(self)
        self.timekeeper = timekeeper
        self.tasks = get_tasks()
        self._callback = _callback
        self.deviceSelect = QComboBox(self)
        self.taskSelect = QComboBox(self)

        # Add items to device select combo box and set initial selection
        self.deviceSelect.addItems(factory.DEVICE_LIST)
        if self.deviceSelect.count() > 0:
            self.deviceSelect.setCurrentIndex(0)  # Set initial value to first option
            self.updateTaskList()  # Update task list based on selected device

        # Connect signals
        self.deviceSelect.currentIndexChanged.connect(self.updateTaskList)
        self.taskSelect.currentIndexChanged.connect(self.updateParameterUI)

        self.initUI()

    def initUI(self):
        # Overall grid layout
        gridLayout = QGridLayout(self)

        # Configuration group at the top
        configurationGroup = QGroupBox("Configuration")
        configurationLayout = QHBoxLayout(configurationGroup)
        configurationLayout.addWidget(QLabel("Select Device:"))
        configurationLayout.addWidget(self.deviceSelect)
        configurationLayout.addWidget(QLabel("Select Task:"))
        configurationLayout.addWidget(self.taskSelect)
        gridLayout.addWidget(configurationGroup, 0, 0, 1, 2)  # Span 1 row, 2 columns

        # Time configuration on the second row, left side
        timeConfigGroup = QGroupBox()
        timeConfigLayout = QHBoxLayout(timeConfigGroup)
        self.timeConfigComboBox = QComboBox(self)
        self.timeConfigComboBox.addItems(["Timestamp", "Duration"])
        timeConfigLayout.addWidget(self.timeConfigComboBox)
        self.setupTimeConfiguration(timeConfigLayout)  # Add time configuration widgets
        gridLayout.addWidget(
            timeConfigGroup, 1, 0
        )  # This will be on the second row, first column

        # Parameter configuration on the second row, right side, taking up two columns
        parameterConfigGroup = QGroupBox("Parameter Configuration")
        parameterConfigLayout = QVBoxLayout(parameterConfigGroup)
        parameterConfigLayout.addWidget(self.parameterConfig)
        gridLayout.addWidget(
            parameterConfigGroup, 1, 1
        )  # This will be on the second row, second column

        # Adjust the column stretch factors according to the desired ratio
        gridLayout.setColumnStretch(
            0, 1
        )  # This sets the stretch factor for the first column
        gridLayout.setColumnStretch(
            1, 2
        )  # This sets the stretch factor for the second column

        # Third row for OK and Cancel buttons
        buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self.okButton)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(self.cancelButton)

        # Add the buttonsLayout to the grid
        gridLayout.addLayout(buttonsLayout, 2, 0, 1, 2)  # Span 1 row and 2 columns

        # Set the layout for the QDialog
        self.setLayout(gridLayout)

        # Style the QDialog

    def updateTimeConfigurationVisibility(self, selection):
        isTimestamp = selection == "Timestamp"
        self.timestampWidget.setVisible(isTimestamp)
        self.durationWidget.setVisible(not isTimestamp)

    def updateTaskList(self):
        # Update the task list based on the selected device
        selected_device = self.deviceSelect.currentText()
        tasks = self.tasks.get(selected_device, {}).keys()
        self.taskSelect.clear()
        self.taskSelect.addItems(tasks)
        if self.taskSelect.count() > 0:
            self.taskSelect.setCurrentIndex(0)  # Set initial value to first option
        # Update parameter UI based on initial selections
        self.updateParameterUI()

    def updateParameterUI(self):
        selected_device = self.deviceSelect.currentText()
        selected_task = self.taskSelect.currentText()
        self.parameterConfig.updateUI(selected_device, selected_task)

    def updateUI(self):
        selected_device = self.deviceSelect.currentText()
        selected_task = self.taskSelect.currentText()
        self.parameterConfig.updateUI(selected_device, selected_task)

    def setupTimeConfiguration(self, layout):
        # Create widgets to hold the grid layouts
        self.timestampWidget = QWidget(self)
        self.durationWidget = QWidget(self)

        # Set grid layouts to these widgets
        timestampGridLayout = self.createDateTimeInputs(datetime.now())
        durationGridLayout = self.createDurationInputs()
        self.timestampWidget.setLayout(timestampGridLayout)
        self.durationWidget.setLayout(durationGridLayout)

        # Add these widgets to the main layout
        layout.addWidget(self.timestampWidget)
        layout.addWidget(self.durationWidget)

        self.updateTimeConfigurationVisibility(self.timeConfigComboBox.currentText())

        # Connect the combobox signal
        self.timeConfigComboBox.currentIndexChanged.connect(
            lambda: self.updateTimeConfigurationVisibility(
                self.timeConfigComboBox.currentText()
            )
        )

    def createDateTimeInputs(self, default_value):
        # Create a grid layout for timestamp inputs
        gridLayout = QGridLayout()
        self.timestampInputs = {}  # Dictionary to hold references to QLineEdit widgets

        # Define the fields and their positions in the grid
        fields = [
            ("Year", "year", 0, 0),
            ("Month", "month", 1, 0),
            ("Day", "day", 2, 0),
            ("Hour", "hour", 0, 1),
            ("Minute", "minute", 1, 1),
            ("Second", "second", 2, 1),
            ("Millisecond", "millisecond", 3, 1),
        ]

        # Add the labels and line edits to the grid layout
        for label_text, field, row, col in fields:
            label = QLabel(f"{label_text}:")
            lineEdit = QLineEdit(self)
            lineEdit.setText(str(getattr(default_value, field, 0)))
            gridLayout.addWidget(label, row, col * 2)
            gridLayout.addWidget(lineEdit, row, col * 2 + 1)
            self.timestampInputs[field] = lineEdit  # Store QLineEdit reference

        return gridLayout

    def createDurationInputs(self):
        # Create a grid layout for duration inputs
        gridLayout = QGridLayout()
        self.durationInputs = {}  # Dictionary to hold references to QLineEdit widgets

        # Define the fields and their positions in the grid
        fields = [
            ("Days", "days", 0, 0),
            ("Hours", "hours", 0, 1),
            ("Minutes", "minutes", 1, 1),
            ("Seconds", "seconds", 2, 1),
            ("Milliseconds", "milliseconds", 3, 1),
        ]

        # Add the labels and line edits to the grid layout
        for label_text, field, row, col in fields:
            label = QLabel(f"{label_text}:")
            lineEdit = QLineEdit(self)
            lineEdit.setText("00")  # Default value set to "00"
            gridLayout.addWidget(label, row, col * 2)
            gridLayout.addWidget(lineEdit, row, col * 2 + 1)
            self.durationInputs[field] = lineEdit  # Store QLineEdit reference

        # Add an empty label to balance the layout
        gridLayout.addWidget(QLabel(""), 2, 0)

        return gridLayout

    def toggleTimeInputs(self):
        # Toggle visibility of time input fields based on selected option
        isTimestamp = bool(self.timeConfigComboBox.currentText().lower() == "timestamp")
        for input in self.timestampInputs:
            input.setVisible(isTimestamp)
        for input in self.durationInputs:
            input.setVisible(not isTimestamp)

    def accept(self):
        # Schedule the task with either timestamp or duration
        selected_device = self.deviceSelect.currentText()
        selected_task = self.taskSelect.currentText()
        schedule_time = self.getDateTimeFromInputs()

        # Retrieve task specifications for the selected task
        task_spec = TASK_USER_INTERFACE_DICTIONARY[selected_device][selected_task]

        # Get parameters from ParameterConfiguration
        params = self.parameterConfig.get_parameters(task_spec)

        # Schedule the job with the retrieved parameters
        if selected_device == DeviceName.DG4202.value:
            self.timekeeper.add_job(
                task_name=selected_task, schedule_time=schedule_time, kwargs=params
            )
        elif selected_device == DeviceName.EDUX1002A.value:
            # Handling for EDUX1002A
            pass

        # Callback to update the UI, etc.
        self._callback()
        super().accept()

    def getDateTimeFromInputs(self):
        # Create a datetime or timedelta object from input fields
        if self.timeConfigComboBox.currentText().lower() == "timestamp":
            # Assuming self.timestampInputs is a dictionary of QLineEdit widgets keyed by field names
            return datetime(
                year=int(self.timestampInputs["year"].text()),
                month=int(self.timestampInputs["month"].text()),
                day=int(self.timestampInputs["day"].text()),
                hour=int(self.timestampInputs["hour"].text()),
                minute=int(self.timestampInputs["minute"].text()),
                second=int(self.timestampInputs["second"].text()),
                microsecond=int(self.timestampInputs["millisecond"].text()) * 1000,
            )
        else:
            # Assuming self.durationInputs is a dictionary of QLineEdit widgets keyed by field names
            duration = timedelta(
                days=int(self.durationInputs["days"].text()),
                hours=int(self.durationInputs["hours"].text()),
                minutes=int(self.durationInputs["minutes"].text()),
                seconds=int(self.durationInputs["seconds"].text()),
                milliseconds=int(self.durationInputs["milliseconds"].text()),
            )
            return datetime.now() + duration

    def getParameters(self):
        # to implement
        return {}


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
