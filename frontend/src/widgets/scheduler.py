import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QDateTimeEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SchedulerWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.dateTimeEdit = QDateTimeEdit(self)
        self.dateTimeEdit.setDateTime(datetime.now())

        self.scheduleButton = QPushButton("Schedule Task", self)
        self.scheduleButton.clicked.connect(self.schedule_task)

        layout = QVBoxLayout(self)
        layout.addWidget(self.dateTimeEdit)
        layout.addWidget(self.scheduleButton)


app_qt = QApplication(sys.argv)
ex = SchedulerWidget()
ex.show()
sys.exit(app_qt.exec_())
