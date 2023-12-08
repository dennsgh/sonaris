from enum import Enum

GRAPH_RGB = (255, 255, 255)


class DeviceName(Enum):
    DG4202 = "DG4202"
    EDUX1002A = "EDUX1002A"


class TaskName(Enum):
    TOGGLE = "Toggle Output"
    SET_WAVEFORM = "Set Waveform Parameters"
    SET_SWEEP = "Set Sweep Parameters"
