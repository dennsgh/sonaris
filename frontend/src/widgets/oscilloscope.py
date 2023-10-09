import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QDoubleSpinBox, QLabel, QPushButton, QGroupBox
from PyQt6.QtCore import QTimer
from device.edux1002a import EDUX1002A, EDUX1002ADetector, EDUX1002AEthernet, EDUX1002AUSB
from pages.templates import ModuleWidget
import header
from widgets.realtimeplot import RealTimePlotWidget


class OscilloscopeWidget(ModuleWidget):

    def __init__(self, oscilloscope: EDUX1002A, channel=1, parent=None):
        super().__init__(parent)
        self.oscilloscope = oscilloscope
        self.channel = channel
        self.tick = 50  # ms
        self.initUI()

    def update_spinbox_values(self, xRange, yRange, x_input, y_input):
        x_input.setValue((xRange[0] + xRange[1]) / 2)
        y_input.setValue((yRange[0] + yRange[1]) / 2)

    def _create_channel_ui(self, channel: int):
        # Creating a group for better organization
        channel_group = QGroupBox(f"{channel}")
        channel_layout = QVBoxLayout()

        plot_widget = pg.PlotWidget()
        plot_widget.setBackground(header.GRAPH_RGB)

        plot_data = plot_widget.plot([], pen="y")
        channel_layout.addWidget(plot_widget)

        # Interactive axis controls
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(QLabel("X-axis:"))

        self.x_input = QDoubleSpinBox()
        self.x_input.setRange(-1e6, 1e6)
        self.x_input.valueChanged.connect(lambda val: plot_widget.setXRange(-val, val))
        axis_layout.addWidget(self.x_input)

        x_zoom_in = QPushButton("+")
        x_zoom_in.clicked.connect(
            lambda: plot_widget.setXRange(*[axis * 0.9 for axis in plot_widget.viewRange()[0]]))
        axis_layout.addWidget(x_zoom_in)

        x_zoom_out = QPushButton("-")
        x_zoom_out.clicked.connect(
            lambda: plot_widget.setXRange(*[axis * 1.1 for axis in plot_widget.viewRange()[0]]))
        axis_layout.addWidget(x_zoom_out)

        axis_layout.addWidget(QLabel("Y-axis:"))

        self.y_input = QDoubleSpinBox()
        self.y_input.setRange(-1e6, 1e6)
        self.y_input.valueChanged.connect(lambda val: plot_widget.setYRange(-val, val))
        axis_layout.addWidget(self.y_input)

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

        plot_widget.setFixedHeight(300)  # Fixed height, adjust as needed
        plot_widget.setBackground('k')  # Black background
        plot_widget.showGrid(x=True, y=True, alpha=0.5)  # Grid with semi-transparency

        # Color and style for the plot axes to make it more oscilloscope-like
        plot_widget.getAxis('left').setTextPen('w')
        plot_widget.getAxis('left').setPen('w')
        plot_widget.getAxis('bottom').setTextPen('w')
        plot_widget.getAxis('bottom').setPen('w')

        # Inside _create_channel_ui
        handler = self.make_range_changed_handler(self.x_input, self.y_input)
        plot_widget.getViewBox().sigRangeChanged.connect(handler)

        return channel_group, plot_data

    def make_range_changed_handler(self, x_input, y_input):

        def handler(viewbox, ranges):
            xRange, yRange = ranges
            self.update_spinbox_values(xRange, yRange, x_input, y_input)

        return handler

    def initUI(self, **kwargs):
        layout = QHBoxLayout()

        channel1_ui, self.plot_data_1 = self._create_channel_ui(1)
        layout.addWidget(channel1_ui)

        channel2_ui, self.plot_data_2 = self._create_channel_ui(2)
        layout.addWidget(channel2_ui)

        self.setLayout(layout)

    def update_data(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    import pyvisa
    # Here you'd initialize your Interface and EDUX1002A class instances.
    rm = pyvisa.ResourceManager()
    oscilloscope = EDUX1002ADetector(rm).detect_device()
    main_window = OscilloscopeWidget(oscilloscope)
    main_window.show()

    sys.exit(app.exec())
