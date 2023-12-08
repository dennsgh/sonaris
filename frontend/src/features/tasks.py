from features.managers import DG4202Manager
from header import DeviceName, TaskName


def task_on_off_dg4202(
    dg4202_manager: DG4202Manager, channel: int, status: bool
) -> bool:
    dg4202_manager.get_device().output_on_off(channel=channel, status=status)
    return True


def task_set_waveform_parameters(
    dg4202_manager: DG4202Manager, channel: int, params: dict
) -> bool:
    dg4202_manager.get_device().set_waveform(channel=channel, params=params)
    return True


def task_set_sweep_parameters(
    dg4202_manager: DG4202Manager, channel: int, params: dict
) -> bool:
    dg4202_manager.get_device().set_sweep_parameters(
        channel=channel, sweep_params=params
    )
    return True


def get_tasks() -> dict:
    """Returns the dict of { device : { task-name : func_pointer , ..} ..}

    Returns:
        dict: dictionary containing devices and its tasks.
    """

    task_dictionary = {
        DeviceName.DG4202.value: {
            TaskName.TOGGLE.value: task_on_off_dg4202,
            TaskName.SET_WAVEFORM.value: task_set_waveform_parameters,
            TaskName.SET_SWEEP.value: task_set_sweep_parameters,
        },
        DeviceName.EDUX1002A.value: {},
    }
    return task_dictionary


TASK_USER_INTERFACE_DICTIONARY = {
    DeviceName.DG4202.value: {
        TaskName.TOGGLE.value: [
            # Example specification
            {"type": "QComboBox", "label": "Channel", "options": ["1", "2"]},
            {"type": "QComboBox", "label": "Switch to", "options": ["ON", "OFF"]},
        ],
        TaskName.SET_WAVEFORM.value: [
            {"type": "QComboBox", "label": "Channel", "options": ["1", "2"]},
            {
                "type": "QComboBox",
                "label": "Waveform Type",
                "options_function": "DG4202.available_waveforms",
            },
            {"type": "QLineEdit", "label": "Frequency (Hz)"},
            {"type": "QLineEdit", "label": "Amplitude"},
            {"type": "QLineEdit", "label": "Offset"},
        ],
        TaskName.SET_SWEEP.value: [
            # ... UI components for sweep parameters
        ],
    },
    DeviceName.EDUX1002A.value: {
        # ... UI specifications for EDUX1002A tasks
    },
}


if __name__ == "__main__":
    print(get_tasks())
