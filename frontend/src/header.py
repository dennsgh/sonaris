from enum import Enum

VERSION_STRING = "v0.1.0"

GRAPH_RGB = (255, 255, 255)
OSCILLOSCOPE_BUFFER_SIZE = 512


class DeviceName(Enum):
    DG4202 = "DG4202"
    EDUX1002A = "EDUX1002A"

    @staticmethod
    def get_name_enum(device_name_str):
        # First, try looking up by name
        try:
            return DeviceName[device_name_str]
        except KeyError:
            pass
        # Next, try looking up by value
        for _, member in DeviceName.__members__.items():
            if member.value == device_name_str:
                return member
        return None


DEVICE_LIST = [DeviceName.DG4202.value, DeviceName.EDUX1002A.value]
NOT_FOUND_STRING = "Device not found!"
TICK_INTERVAL = 500.0  # in ms

DEFAULT_TAB_STYLE = {"height": "30px", "padding": "2px"}
