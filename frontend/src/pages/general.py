from features.managers import DG4202Manager, EDUX1002AManager
from PyQt6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget
from widgets.dg_default import DG4202DefaultWidget
from widgets.oscilloscope import OscilloscopeWidget

NOT_FOUND_STRING = "Device not found!"
TIMER_INTERVAL = 1000.0  # in ms
TIMER_INTERVAL_S = TIMER_INTERVAL / 1000.0  # in ms

DEFAULT_TAB_STYLE = {"height": "30px", "padding": "2px"}


class GeneralPage(QWidget):
    def check_connection(self) -> bool:
        self.my_generator = self.dg4202_manager.get_device()
        self.all_parameters = self.dg4202_manager.data_source.query_data()
        if self.my_generator is not None:
            is_alive = self.my_generator.is_connection_alive()
            if not is_alive:
                self.my_generator = None
            return is_alive
        return False

    def __init__(
        self,
        dg4202_manager: DG4202Manager,
        edux1002a_manager: EDUX1002AManager,
        parent=None,
        args_dict: dict = None,
    ):
        super().__init__(parent=parent)
        self.dg4202_manager = dg4202_manager
        self.args_dict = args_dict
        self.edux1002a_manager = edux1002a_manager
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.check_connection()
        self.connection_status_label = QLabel(
            f"Connection Status: {self.all_parameters.get('connected', 'Not connected')}"
        )
        self.main_layout.addWidget(self.connection_status_label)
        self.oscilloscope = OscilloscopeWidget(self.edux1002a_manager)
        self.main_layout.addWidget(self.oscilloscope)
        self.status_label = QLabel("")
        self.main_layout.addWidget(self.status_label)

        # Create the tab widget
        self.tab_widget = QTabWidget()

        # Default Widget Tab
        self.default_widget = DG4202DefaultWidget(
            self.dg4202_manager, self, self.args_dict
        )
        self.tab_widget.addTab(self.default_widget, "Default Mode")

        # Adding the tab widget to the main layout
        self.main_layout.addWidget(self.tab_widget)

        self.setLayout(self.main_layout)
