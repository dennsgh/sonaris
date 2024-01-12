from pages import factory

"""
These tasks are used by the scheduler, they are wrappers for the scheduler to call the manager objects.
You will have to point to them under header.py
"""


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


def task_set_sweep_parameters(
    channel: int,
    fstart: float,
    fstop: float,
    time: float,
    rtime: float = 0,
    htime_start: float = 0,
    htime_stop: float = 0,
) -> bool:
    params = {
        "FSTART": fstart,
        "FSTOP": fstop,
        "TIME": time,
        "RTIME": rtime,
        "HTIME_START": htime_start,
        "HTIME_STOP": htime_stop,
    }
    factory.dg4202_manager.get_device().set_sweep_parameters(
        channel=channel, sweep_params=params
    )
    return True


def task_auto_edux1002a(kwarg_value):
    # for testing, kwarg_value means nothing
    factory.edux1002a_manager.get_device().autoscale()
    return True
