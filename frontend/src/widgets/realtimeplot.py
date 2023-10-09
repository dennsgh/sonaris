import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import header
import abc


class DataSource(abc.ABC):

    def get_data(self):
        # This method should return the time and data for the requested channel.
        return [], []


class RealTimePlotWidget(pg.PlotWidget):

    def __init__(self, data_source=None, window_width=500):
        super().__init__()

        self.data_source = data_source or DataSource()
        self.window_width = window_width
        self.tick = 50
        self.curve = self.plot()
        self.Xm = np.linspace(0, 0, self.window_width)
        self.ptr = self.window_width

        # Design elements to resemble oscilloscope
        self.setBackground(header.GRAPH_RGB)
        # Timer for updating plot
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.tick)  # Adjust this value as per your requirements

    def update_plot(self):
        self.Xm[:-1] = self.Xm[1:]
        time, value = self.data_source.get_data()
        #self.Xm[-1] = float(value)
        self.ptr += 1
        self.curve.setData(self.Xm)
        self.curve.setPos(self.ptr, 0)

    def freeze(self):
        self.timer.stop()

    def unfreeze(self):
        self.timer.start(self.tick)