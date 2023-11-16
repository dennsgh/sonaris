from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QHBoxLayout
from pages import dg4202, factory, settings
import argparse
from qt_material import apply_stylesheet
from typing import Dict, Optional
import sys
from features.managers import DG4202Manager, StateManager, EDUX1002AManager
from features.scheduler import Scheduler
import pyvisa
from widgets.sidebar import Sidebar
from widgets.oscilloscope import OscilloscopeWidget
from widgets.templates import *
from widgets.menu import MainMenuBar
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QIcon, QAction
OSCILLOSCOPE_BUFFER_SIZE = 512


def signal_handler(signal, frame):
    print("Exit signal detected.")
    # Perform additional error handling actions here if needed
    sys.exit(0)


def init_managers(args_dict: dict):
    factory.resource_manager = pyvisa.ResourceManager()
    factory.state_manager = StateManager()
    factory.edux1002a_manager = EDUX1002AManager(state_manager=factory.state_manager,
                                                 args_dict=args_dict,
                                                 resource_manager=factory.resource_manager,
                                                 buffer_size=OSCILLOSCOPE_BUFFER_SIZE)
    factory.dg4202_manager = DG4202Manager(factory.state_manager,
                                           args_dict=args_dict,
                                           resource_manager=factory.resource_manager)
    factory.DG4202SCHEDULER: Scheduler(function_map=factory.dg4202_manager.function_map,
                                       interval=0.001)
    factory.state_manager.write_state({'dg_last_alive': None})


class MainWindow(ModularMainWindow):

    def __init__(self, args_dict: dict) -> None:
        super().__init__()
        menu_bar = MainMenuBar(self)
        self.setWindowTitle("MRI Labs")
        self.setMenuBar(menu_bar)
        # ---------------------------------------------------------------------- #
        # ---------------------------SIDEBAR SETUP------------------------------ #
        self.sidebar = Sidebar(self)
        self.sidebar_dict: Dict[str, QWidget] = {
            "DG4202": dg4202.DG4202Page(factory.dg4202_manager, self, args_dict=args_dict),
            "Settings": settings.SettingsPage(self, args_dict),
        }
        self.sidebar.addItems(self.sidebar_dict.keys())  # Add strings to sidebar items
        self.sidebar_content = QStackedWidget(self)
        list(map(self.sidebar_content.addWidget,
                 self.sidebar_dict.values()))  # Adds all child widgets to content widgets

        # ---------------------------OSCILLOSCOPE------------------------------ #
        self.oscilloscope = OscilloscopeWidget(factory.edux1002a_manager)

        # --------------------------------------------------------------------- #
        # ---------------------------LAYOUT SETUP------------------------------ #
        # --------------------------------------------------------------------- #

        self.add_widget_to_left(self.sidebar)
        self.add_widget_to_middle(self.sidebar_content)  # Use the method from ModularMainWindow
        self.add_widget_to_top(self.oscilloscope)  # Use the method from ModularMainWindow
        # Connect the Sidebar's custom signal to the MainWindow's slot
        self.sidebar.pageSelected.connect(self.loadPage)

    def loadPage(self, page_name: str) -> None:
        page_widget: Optional[QWidget] = self.sidebar_dict.get(page_name)
        if page_widget:
            self.sidebar_content.setCurrentWidget(page_widget)


def create_app(args_dict: dict) -> (QApplication, QMainWindow):
    init_managers(args_dict=args_dict)

    app = QApplication([])
    window = MainWindow(args_dict)
    apply_stylesheet(app, theme='dark_blue.xml')
    window.setWindowTitle("mrilabs")
    window.show()
    return app, window


def run_application():

    parser = argparse.ArgumentParser(description="Run the mrilabs application.")
    parser.add_argument('--hardware-mock',
                        action='store_true',
                        help="Run the app in hardware mock mode.")
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Run the application in debug mode.')
    parser.add_argument('--api-server',
                        type=int,
                        help="Launch an api server on the specified port.")
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=8501,
                        help="Specify the port number to run on. Defaults to 8501.")
    parser.add_argument(
        '--env',
        type=str,
        default='development',
        choices=['development', 'production'],
        help="Specify the environment to run the application in. Defaults to development.")

    args = parser.parse_args()
    args_dict = vars(args)
    print(args_dict)
    app, window = create_app(args_dict)
    app.exec()


if __name__ == "__main__":
    run_application()
