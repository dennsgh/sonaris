import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QDoubleSpinBox, QLabel, QPushButton, QGroupBox
from PyQt6.QtCore import QTimer
from device.edux1002a import EDUX1002A, EDUX1002ADetector, EDUX1002AEthernet, EDUX1002AUSB
from pages.templates import ModuleWidget
# Assuming your EDUX1002A class and Interface class are already defined...


class OscilloscopeWidget(ModuleWidget):

    def __init__(self, oscilloscope: EDUX1002A, channel=1, parent=None):
        super().__init__(parent)
        self.oscilloscope = oscilloscope
        self.channel = channel
        self.tick = 50  # ms
        self.initUI()

    def _create_channel_ui(self, channel_name):
        # Creating a group for better organization
        channel_group = QGroupBox(channel_name)

        # Vertical layout for each channel
        channel_layout = QVBoxLayout()

        # Setup plot for the channel
        plot_widget = pg.PlotWidget()
        plot_data = plot_widget.plot([], pen="y")
        channel_layout.addWidget(plot_widget)

        # Interactive axis controls
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("X-axis:"))

        x_input = QDoubleSpinBox()
        x_input.setRange(-1e6, 1e6)
        x_input.valueChanged.connect(lambda val: plot_widget.setXRange(-val, val))
        axis_layout.addWidget(x_input)

        x_zoom_in = QPushButton("+")
        x_zoom_in.clicked.connect(
            lambda: plot_widget.setXRange(*[axis * 0.9 for axis in plot_widget.viewRange()[0]]))
        axis_layout.addWidget(x_zoom_in)

        x_zoom_out = QPushButton("-")
        x_zoom_out.clicked.connect(
            lambda: plot_widget.setXRange(*[axis * 1.1 for axis in plot_widget.viewRange()[0]]))
        axis_layout.addWidget(x_zoom_out)

        axis_layout.addWidget(QLabel("Y-axis:"))

        y_input = QDoubleSpinBox()
        y_input.setRange(-1e6, 1e6)
        y_input.valueChanged.connect(lambda val: plot_widget.setYRange(-val, val))
        axis_layout.addWidget(y_input)

        y_zoom_in = QPushButton("+")
        y_zoom_in.clicked.connect(
            lambda: plot_widget.setYRange(*[axis * 0.9 for axis in plot_widget.viewRange()[1]]))
        axis_layout.addWidget(y_zoom_in)

        y_zoom_out = QPushButton("-")
        y_zoom_out.clicked.connect(
            lambda: plot_widget.setYRange(*[axis * 1.1 for axis in plot_widget.viewRange()[1]]))
        axis_layout.addWidget(y_zoom_out)

        channel_layout.addLayout(axis_layout)
        channel_group.setLayout(channel_layout)

        return channel_group, plot_data

    def initUI(self, **kwargs):
        layout = QHBoxLayout()

        channel1_ui, self.plot_data_1 = self._create_channel_ui("Channel 1")
        layout.addWidget(channel1_ui)

        channel2_ui, self.plot_data_2 = self._create_channel_ui("Channel 2")
        layout.addWidget(channel2_ui)

        self.setLayout(layout)

    def update_data(self):
        # Fetch data from oscilloscope
        # waveform = self.oscilloscope.get_waveform()
        pass
        # For simplicity, let's assume waveform is a list of y-values.
        # You may need to adjust based on actual data format.
        # y_data = np.array(waveform)
        # x_data = np.arange(len(y_data))

        #self.plot_data.setData(x_data, y_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Here you'd initialize your Interface and EDUX1002A class instances.
    oscilloscope = EDUX1002ADetector.detect_device()

    main_window = OscilloscopeWidget(oscilloscope)
    main_window.show()

    sys.exit(app.exec())
