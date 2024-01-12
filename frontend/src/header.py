from enum import Enum

GRAPH_RGB = (255, 255, 255)
OSCILLOSCOPE_BUFFER_SIZE = 512


class DeviceName(Enum):
    DG4202 = "DG4202"
    EDUX1002A = "EDUX1002A"


class TaskName(Enum):
    DG4202_TOGGLE = "Toggle Output"
    DG4202_SET_WAVEFORM = "Set Waveform Parameters"
    DG4202_SET_SWEEP = "Set Sweep Parameters"
    EDUX1002A_AUTO = "Press Auto"
