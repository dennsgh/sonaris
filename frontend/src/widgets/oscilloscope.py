import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QDoubleSpinBox, QLabel, QPushButton, QGroupBox
from PyQt6.QtCore import QTimer
from device.edux1002a import EDUX1002A, EDUX1002ADetector, EDUX1002AEthernet, EDUX1002AUSB
from widgets.templates import ModuleWidget
import header
from widgets.realtimeplot import RealtimeDisplay
from device.data import DataBuffer
from features.managers import EDUX1002AManager


class OscilloscopeWidget(ModuleWidget):

    def __init__(self, edux1002a_manager: EDUX1002AManager, parent=None, tick: int = 200):
        super().__init__(parent)
        self.edux1002a_manager = edux1002a_manager
        self.tick = tick  # ms, for now, you can adjust this
        self.x_input = {1: None, 2: None}
        self.y_input = {1: None, 2: None}
        self.initUI()

        # Timer setup for real-time data update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(self.tick)

    def update_spinbox_values(self, xRange, yRange, x_input, y_input):
        x_input.blockSignals(True)
        y_input.blockSignals(True)

        x_input.setValue((xRange[0] + xRange[1]) / 2)
        y_input.setValue((yRange[0] + yRange[1]) / 2)

        x_input.blockSignals(False)
        y_input.blockSignals(False)

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

        self.x_input[channel] = QDoubleSpinBox()
        self.x_input[channel].setRange(-1e6, 1e6)
        self.x_input[channel].valueChanged.connect(lambda val: (plot_widget.setXRange(
            -val, val), self.x_input[channel].blockSignals(True), self.x_input[channel].setValue(
                val), self.x_input[channel].blockSignals(False)))

        axis_layout.addWidget(self.x_input[channel])

        x_zoom_in = QPushButton("+")
        x_zoom_in.clicked.connect(lambda: (plot_widget.blockSignals(
            True), plot_widget.setXRange(*[axis * 0.9 for axis in plot_widget.viewRange()[0]]),
                                           plot_widget.blockSignals(False)))

        axis_layout.addWidget(x_zoom_in)

        x_zoom_out = QPushButton("-")
        # For X-axis zoom out button:
        x_zoom_out.clicked.connect(lambda: (plot_widget.blockSignals(
            True), plot_widget.setXRange(*[axis * 1.1 for axis in plot_widget.viewRange()[0]]),
                                            plot_widget.blockSignals(False)))
        axis_layout.addWidget(x_zoom_out)

        axis_layout.addWidget(QLabel("Y-axis:"))

        self.y_input[channel] = QDoubleSpinBox()
        self.y_input[channel].setRange(-1e6, 1e6)
        # For Y-axis spinbox:
        self.y_input[channel].valueChanged.connect(lambda val: (plot_widget.setYRange(
            -val, val), self.y_input[channel].blockSignals(True), self.y_input[channel].setValue(
                val), self.y_input[channel].blockSignals(False)))

        y_zoom_in = QPushButton("+")
        y_zoom_in.clicked.connect(lambda: (plot_widget.blockSignals(
            True), plot_widget.setYRange(*[axis * 0.9 for axis in plot_widget.viewRange()[1]]),
                                           plot_widget.blockSignals(False)))
        axis_layout.addWidget(y_zoom_in)

        y_zoom_out = QPushButton("-")
        y_zoom_out.clicked.connect(lambda: (plot_widget.blockSignals(
            True), plot_widget.setYRange(*[axis * 1.1 for axis in plot_widget.viewRange()[1]]),
                                            plot_widget.blockSignals(False)))
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
        handler = self.make_range_changed_handler(self.x_input[channel], self.y_input[channel])
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
        # Create the freeze/unfreeze button
        self.freeze_button = QPushButton("Freeze")
        self.freeze_button.clicked.connect(self.toggle_freeze)
        layout.addWidget(self.freeze_button)
        self.setLayout(layout)

    def update_data(self):
        try:
            self.edux1002a_manager.buffer_ch1.update()
            self.edux1002a_manager.buffer_ch2.update()

            y1_data = self.edux1002a_manager.buffer_ch1.get_data()
            y2_data = self.edux1002a_manager.buffer_ch2.get_data()
            x1_data = np.arange(len(y1_data))
            x2_data = np.arange(len(y2_data))

            # Here we'll update both channels. If you want only one channel or different data for different channels, you'll need to modify this:
            self.plot_data_1.setData(x1_data, y1_data)
            self.plot_data_2.setData(x2_data, y2_data)
        except Exception as e:
            print(f"[Oscilloscope]{e}")
            self.freeze()

    def freeze(self):
        """Stop updating the waveform"""
        self.freeze_button.setText("Unfreeze")
        self.timer.stop()

    def unfreeze(self):
        """Resume updating the waveform"""
        self.timer.start(self.tick)
        self.freeze_button.setText("Freeze")

    def toggle_freeze(self):
        if self.timer.isActive():
            self.freeze()
        else:
            self.unfreeze()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    import pyvisa
    # Here you'd initialize your Interface and EDUX1002A class instances.
    rm = pyvisa.ResourceManager()
    oscilloscope = EDUX1002ADetector(rm).detect_device()
    main_window = OscilloscopeWidget(oscilloscope)
    main_window.show()

    sys.exit(app.exec())
