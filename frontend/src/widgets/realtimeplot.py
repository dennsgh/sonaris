import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from device.data import DataSource, DataBuffer
from widgets.templates import ModuleWidget


class RealtimeDisplay(ModuleWidget):

    def __init__(self, buffer: DataBuffer, tick: int = 200):
        super().__init__()
        self.buffer = buffer
        self.tick = tick
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Setup pyqtgraph widget
        self.plot_widget = pg.PlotWidget(background='k')  # white background
        #self.plot_widget.setLabel('left', 'Voltage', color='black', size=20)
        #self.plot_widget.setLabel('bottom', 'Time', color='black', size=20)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)

        # Control Panel
        main_layout.addWidget(self.plot_widget)
        self.setLayout(main_layout)

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color="w",
                                                        width=2))  # default color red, width 2
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(self.tick)  # Update every 100 ms

    def update_waveform(self):
        self.buffer.update()

        y_data = self.buffer.get_data()
        x_data = np.arange(len(y_data))

        self.curve.setData(x_data, y_data)
        self.plot_widget.autoRange()

    def freeze(self):
        self.timer.stop()

    def unfreeze(self):
        self.timer.start(self.tick)


if __name__ == "__main__":
    # Detect the device
    from device.edux1002a import EDUX1002ADetector, EDUX1002ADataSource
    import pyvisa
    app = QApplication(sys.argv)
    rm = pyvisa.ResourceManager()
    device = EDUX1002ADetector(resource_manager=rm).detect_device()
    if device:
        device.setup_waveform_readout()
        device.get_waveform_data()
        data_source = EDUX1002ADataSource(
            device)  # for now leave it to tap into the default ( channel 1 by default )
        data_buffer = DataBuffer(data_source, 32)

        main_window = RealtimeDisplay(data_buffer)
        main_window.show()
        sys.exit(app.exec())
    else:
        print("No EDUX1002A device detected.")
