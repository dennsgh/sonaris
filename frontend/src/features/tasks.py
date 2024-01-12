from features.managers import DG4202Manager
from header import DeviceName, TaskName
from pages import factory


def task_on_off_dg4202(channel: int, status: bool) -> bool:
    factory.dg4202_manager.get_device().output_on_off(channel=channel, status=status)
    return True


def task_set_waveform_parameters(
    channel: int,
    waveform_type: str,
    amplitude: float,
    frequency: float,
    offset: float,
) -> bool:
    factory.dg4202_manager.get_device().set_waveform(
        channel=channel,
        waveform_type=waveform_type,
        amplitude=amplitude,
        frequency=frequency,
        params=None,
        offset=offset,
    )
    return True


def task_set_sweep_parameters(channel: int, params: dict) -> bool:
    factory.dg4202_manager.get_device().set_sweep_parameters(
        channel=channel, sweep_params=params
    )
    return True


def task_auto_edux1002a(kwarg_value):
    # for testing
    return


def get_tasks() -> dict:
    """Returns the dict of { device : { task-name : func_pointer , ..} ..}

    Returns:
        dict: dictionary containing devices and its tasks.
    """

    task_dictionary = {
        DeviceName.DG4202.value: {
            TaskName.DG4202_TOGGLE.value: task_on_off_dg4202,
            TaskName.DG4202_SET_WAVEFORM.value: task_set_waveform_parameters,
            TaskName.DG4202_SET_SWEEP.value: task_set_sweep_parameters,
        },
        DeviceName.EDUX1002A.value: {
            TaskName.EDUX1002A_AUTO.value: task_auto_edux1002a
        },
    }
    return task_dictionary


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
        TaskName.DG4202_SET_SWEEP.value: [{}],
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


if __name__ == "__main__":
    print(get_tasks())
