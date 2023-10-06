from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QHBoxLayout
from pages import home, dg4202, factory
import argparse
from qt_material import apply_stylesheet
from typing import Dict, Optional

from features.state_managers import DG4202Manager, StateManager
from features.scheduler import Scheduler


def init_managers(args_dict: dict):
    factory.state_manager = StateManager()
    factory.dg4202_manager = DG4202Manager(factory.state_manager, args_dict=args_dict)
    factory.DG4202SCHEDULER: Scheduler(function_map=factory.dg4202_manager.function_map,
                                       interval=0.001)
    factory.state_manager.write_state({'last_known_device_uptime': None})


class MainWindow(QMainWindow):

    def __init__(self, args_dict: dict) -> None:
        super().__init__()
        self.setWindowTitle("mrilabs")

        # Main horizontal layout
        self.mainLayout = QHBoxLayout()

        # Sidebar on the left
        self.sidebar: QListWidget = QListWidget(self)
        self.sidebar.setMaximumWidth(200)
        # Assuming HomePage and DG4202Page both inherit from QWidget
        self.child_windows: Dict[str, QWidget] = {
            "Home": home.HomePage(self, args_dict),
            "DG4202": dg4202.DG4202Page(self, args_dict=args_dict)
        }
        self.stacked_widget: QStackedWidget = QStackedWidget(self)
        list(map(self.stacked_widget.addWidget,
                 self.child_windows.values()))  # Adds all child pages

        self.sidebar.addItems(self.child_windows.keys())
        self.mainLayout.addWidget(self.sidebar)

        # Vertical layout for the stacked widget (if you want to add anything else vertically next to the stacked widget)
        self.layout = QVBoxLayout()
        self.mainLayout.addLayout(self.layout)

        # Add more pages to the stacked_widget as needed...
        self.layout.addWidget(self.stacked_widget)

        container: QWidget = QWidget(self)
        container.setLayout(self.mainLayout)  # Use mainLayout here
        self.setCentralWidget(container)

        self.sidebar.itemClicked.connect(self.loadPage)

    def loadPage(self, item: QListWidgetItem) -> None:
        page_name: str = item.text()
        page_widget: Optional[QWidget] = self.child_windows.get(page_name)
        if page_widget:
            self.stacked_widget.setCurrentWidget(page_widget)


def create_app(args_dict: dict) -> (QApplication, QMainWindow):
    init_managers(args_dict=args_dict)

    app = QApplication([])
    window = MainWindow(args_dict)
    apply_stylesheet(app, theme='dark_teal.xml')
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
