from features.managers import DG4202Manager


def task_on_off_dg4202(
    dg4202_manager: DG4202Manager, channel: int, status: bool
) -> bool:
    dg4202_manager.get_device().output_on_off(channel=channel, status=status)
    return True


def set_waveform_parameters(
    dg4202_manager: DG4202Manager, channel: int, params: dict
) -> bool:
    dg4202_manager.get_device().set_waveform(channel=channel, params=params)
    return True


def set_sweep_parameters(
    dg4202_manager: DG4202Manager, channel: int, params: dict
) -> bool:
    dg4202_manager.get_device().set_sweep_parameters(
        channel=channel, sweep_params=params
    )
    return True
