from enum import Enum

from features.tasks import (
    task_auto_edux1002a,
    task_on_off_dg4202,
    task_set_sweep_parameters,
    task_set_waveform_parameters,
)

VERSION_STRING = "v0.1.0"

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


DEVICE_LIST = [DeviceName.DG4202.value, DeviceName.EDUX1002A.value]
NOT_FOUND_STRING = "Device not found!"
TICK_INTERVAL = 1000.0  # in ms

DEFAULT_TAB_STYLE = {"height": "30px", "padding": "2px"}

"""
The task list is read by the job_scheduler module and app.py to register the task and render the UI.
"""

TASK_LIST_DICTIONARY = {
    DeviceName.DG4202.value: {
        TaskName.DG4202_TOGGLE.value: task_on_off_dg4202,
        TaskName.DG4202_SET_WAVEFORM.value: task_set_waveform_parameters,
        TaskName.DG4202_SET_SWEEP.value: task_set_sweep_parameters,
    },
    DeviceName.EDUX1002A.value: {TaskName.EDUX1002A_AUTO.value: task_auto_edux1002a},
}


# These refer to header.py for uniformity!
TASK_USER_INTERFACE_DICTIONARY = {
    DeviceName.DG4202.value: {
        TaskName.DG4202_TOGGLE.value: [
            {
                "type": "QComboBox",
                "label": "Channel",
                "kwarg_label": "channel",
                "options": ["1", "2"],
                "data_type": "int",
            },
            {
                "type": "QComboBox",
                "label": "Switch to",
                "options": ["ON", "OFF"],
                "kwarg_label": "status",
                "data_type": "str",
            },
        ],
        TaskName.DG4202_SET_WAVEFORM.value: [
            {
                "type": "QComboBox",
                "label": "Channel",
                "kwarg_label": "channel",
                "options": ["1", "2"],
                "data_type": "int",
            },
            {
                "type": "QComboBox",
                "label": "Waveform Type",
                "kwarg_label": "waveform_type",
                "options_function": "DG4202.available_waveforms",  # refers to driver DG4202 class and its method to get the list of waveforms.
                "data_type": "str",
            },
            {
                "type": "QLineEdit",
                "label": "Frequency (Hz)",
                "kwarg_label": "frequency",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Amplitude",
                "kwarg_label": "amplitude",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Offset",
                "kwarg_label": "offset",
                "data_type": "float",
            },
        ],
        TaskName.DG4202_SET_SWEEP.value: [
            {
                "type": "QComboBox",
                "label": "Channel",
                "kwarg_label": "channel",
                "options": ["1", "2"],
                "data_type": "int",
            },
            {
                "type": "QLineEdit",
                "label": "Freq Start",
                "kwarg_label": "fstart",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Freq Stop",
                "kwarg_label": "fstop",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Time",
                "kwarg_label": "time",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Return",
                "kwarg_label": "rtime",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Start Hold",
                "kwarg_label": "htime_start",
                "data_type": "float",
            },
            {
                "type": "QLineEdit",
                "label": "Stop Hold",
                "kwarg_label": "htime_stop",
                "data_type": "float",
            },
        ],
    },
    DeviceName.EDUX1002A.value: {
        TaskName.EDUX1002A_AUTO.value: [
            {
                "type": "QComboBox",
                "label": "kwarg_value",
                "kwarg_label": "kwarg_value",
                "options": ["Press", "NoPress"],
                "data_type": "str",
            },
        ],
    },
}


def get_tasks() -> dict:
    """Returns the dict of { device : { task-name : func_pointer , ..} ..}

    Returns:
        dict: dictionary containing devices and its tasks.
    """

    return TASK_LIST_DICTIONARY
