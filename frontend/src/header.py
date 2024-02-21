from enum import Enum

VERSION_STRING = "v0.1.0"

GRAPH_RGB = (255, 255, 255)
OSCILLOSCOPE_BUFFER_SIZE = 512


class DeviceName(Enum):
    DG4202 = "DG4202"
    EDUX1002A = "EDUX1002A"

    @staticmethod
    def get_task_name_enum(device_name_str):
        try:
            return DeviceName[device_name_str]
        except KeyError:
            return None


DEVICE_LIST = [DeviceName.DG4202.value, DeviceName.EDUX1002A.value]
NOT_FOUND_STRING = "Device not found!"
TICK_INTERVAL = 500.0  # in ms

DEFAULT_TAB_STYLE = {"height": "30px", "padding": "2px"}
