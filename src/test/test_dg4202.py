from unittest.mock import Mock, call

import pytest

from sonaris.device.dg4202 import DG4202


@pytest.fixture
def mock_interface():
    interface = Mock()
    return interface


def test_set_waveform(mock_interface):
    device = DG4202(mock_interface)

    for channel in range(1, 3):
        # Reset mock for a clean state in each iteration
        mock_interface.reset_mock()

        # Act: Call set_waveform to set type to "SIN"
        device.set_waveform(channel=channel, waveform_type="SIN")

        # Assert: Verify all expected calls were made
        expected_calls = [
            call.write(f"SOURce{channel}:FUNCtion SIN"),
            call.write(
                f"SOURce{channel}:FREQuency:FIXed 0.0"
            ),  # Assuming default frequency is set even when not specified
        ]
        mock_interface.assert_has_calls(expected_calls, any_order=False)

        # Reset mock for the next set of operations
        mock_interface.reset_mock()

        # Act: Set frequency to 1000 Hz
        device.set_waveform(channel=channel, frequency=1000)

        # Assert: Verify the call to set frequency was made
        mock_interface.write.assert_called_with(f"SOURce{channel}:FREQuency:FIXed 1000")


def test_turn_off_modes(mock_interface):
    device = DG4202(mock_interface)
    calls = []
    for channel in range(1, 3):

        device.turn_off_modes(channel=channel)
        calls += [
            call(f"SOURce{channel}:SWEEp:STATe OFF"),
            call(f"SOURce{channel}:BURSt:STATe OFF"),
            call(f"SOURce{channel}:MOD:STATe OFF"),
        ]

    mock_interface.write.assert_has_calls(calls)


def test_check_status(mock_interface):
    mock_interface.read.return_value = "SomeStatus"
    device = DG4202(mock_interface)
    status = device.check_status()
    assert status == "SomeStatus"


def test_output_on_off(mock_interface):
    device = DG4202(mock_interface)

    for channel in range(1, 3):
        device.output_on_off(channel=channel, status=True)
        mock_interface.write.assert_called_with(f"OUTPut{channel} ON")

        device.output_on_off(channel=channel, status=False)
        mock_interface.write.assert_called_with(f"OUTPut{channel} OFF")


def test_set_mode(mock_interface):
    device = DG4202(mock_interface)

    mode_to_command = {
        "sweep": "SWEEp:STATe ON",
        "burst": "BURSt:STATe ON",
        "mod": "MOD:STATe ON",
    }

    for channel in range(1, 3):  # Assuming channels 1 and 2
        for mode, command in mode_to_command.items():
            device.set_mode(channel=channel, mode=mode)
            mock_interface.write.assert_called_with(f"SOURce{channel}:{command}")
            # Reset mock calls for the next iteration
            mock_interface.write.reset_mock()


def test_is_connection_alive(mock_interface):
    mock_interface.read.return_value = "SIN"
    device = DG4202(mock_interface)

    # Test for alive connection
    assert device.is_connection_alive() == True

    # Test for dead connection
    mock_interface.read.side_effect = Exception("Connection lost")
    assert device.is_connection_alive() == False
