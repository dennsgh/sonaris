import sys

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from device.edux1002a import EDUX1002A, EDUX1002ADetector

# Assuming your EDUX1002A class and Interface class are already defined...


class OscilloscopeApp(QMainWindow):
    def __init__(self, oscilloscope: EDUX1002A, channel=1):
        super().__init__()

        self.oscilloscope = oscilloscope
        self.channel = channel
        self.tick = 50  # ms
        # Set up GUI
        self.setWindowTitle("Real-time Oscilloscope Display")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Create pyqtgraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_data = self.plot_widget.plot([], pen="y")
        layout.addWidget(self.plot_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up a QTimer to fetch data from oscilloscope regularly
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(self.tick)  # Update every 50ms. Adjust as needed.

    def update_data(self):
        # Fetch data from oscilloscope
        waveform = self.oscilloscope.get_waveform()

        # For simplicity, let's assume waveform is a list of y-values.
        # You may need to adjust based on actual data format.
        y_data = np.array(waveform)
        x_data = np.arange(len(y_data))

        self.plot_data.setData(x_data, y_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Here you'd initialize your Interface and EDUX1002A class instances.
    oscilloscope = EDUX1002ADetector.detect_device()

    main_window = OscilloscopeApp(oscilloscope)
    main_window.show()

    sys.exit(app.exec())
