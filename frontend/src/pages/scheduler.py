from pages import factory
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from widgets.job_scheduler import SchedulerWidget

from scheduler.timekeeper import Timekeeper


class SchedulerPage(QWidget):
    def __init__(
        self,
        args_dict: dict,
        parent=None,
        timekeeper: Timekeeper = None,
    ):
        super().__init__(parent=parent)
        self.args_dict = args_dict
        self.timekeeper = timekeeper or factory.timekeeper
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.scheduler_widget = SchedulerWidget(self.timekeeper)
        # Adding the tab widget to the main layout
        self.main_layout.addWidget(self.scheduler_widget)

        self.setLayout(self.main_layout)
