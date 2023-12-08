from datetime import datetime, timedelta

from features.tasks import get_tasks
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
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from widgets.parameters import ParameterConfiguration

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
        self.resize(800, 640)
        self.parameterConfig = ParameterConfiguration(self)
        self.timekeeper = timekeeper
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
        # Show or hide time inputs based on the combobox selection
        isTimestamp = selection == "Timestamp"
        for input in self.timeInputs:
            input.setVisible(isTimestamp)

    def updateTaskList(self):
        # Update the task list based on the selected device
        selected_device = self.deviceSelect.currentText()
        tasks = get_tasks().get(selected_device, {}).keys()
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
        # You might need to adjust the logic here to align with the new combobox selection.
        # For now, let's just create the inputs based on the current selection.
        self.timeInputs = self.createDateTimeInputs(datetime.now())
        for input in self.timeInputs:
            layout.addWidget(input)
        self.updateTimeConfigurationVisibility(self.timeConfigComboBox.currentText())

        # Connect the signal of the combobox to update the visibility of the time inputs
        self.timeConfigComboBox.currentIndexChanged.connect(
            lambda: self.updateTimeConfigurationVisibility(
                self.timeConfigComboBox.currentText()
            )
        )

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
            params = self.getParameters()
            self.timekeeper.add_job(task_name, schedule_time, **params)
        elif selected_device == DeviceName.EDUX1002A.value:
            # Handling for EDUX1002A
            pass

        super().accept()

    def getParameters(self):
        # to implement
        return {}

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
