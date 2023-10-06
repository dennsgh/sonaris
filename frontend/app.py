from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QVBoxLayout, QListWidget
from PyQt6.QtWidgets import QStackedWidget
from pages import home, dg4202
import argparse
from qt_material import apply_stylesheet


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("mrilabs")

        self.layout = QVBoxLayout()
        self.sidebar = QListWidget()
        self.sidebar.addItem("Home")
        self.sidebar.addItem("DG4202")

        self.layout.addWidget(self.sidebar)
        self.child_windows = {"Home": home.HomePage(), "DG4202": dg4202.DG4202Page()}
        self.stacked_widget = QStackedWidget()
        list(map(self.stacked_widget.addWidget,
                 self.child_windows.values()))  # Adds all child pages

        # Add more pages to the stacked_widget as needed...

        self.layout.addWidget(self.stacked_widget)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.sidebar.itemClicked.connect(self.loadPage)

    def loadPage(self, item):
        page_name = item.text()
        page_widget = self.child_windows.get(page_name)
        if page_widget:
            self.stacked_widget.setCurrentWidget(page_widget)


def create_app(args_dict: dict) -> (QApplication, QMainWindow):

    app = QApplication([])
    window = MainWindow()
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
