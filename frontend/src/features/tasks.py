from typing import List, Tuple

from features.managers import DG4202Manager


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


def get_tasks() -> List[Tuple]:
    """Returns the (name,func_pointer) list of tuples

    Returns:
        List[Tuple]: list of tuples containing function name and its pointer
    """
    task_functions = [
        task_on_off_dg4202,
        task_set_waveform_parameters,
        task_set_sweep_parameters,
    ]
    task_tuples = [(func.__name__, func) for func in task_functions]
    return task_tuples


if __name__ == "__main__":
    print(get_tasks())
