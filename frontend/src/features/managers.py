import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pyvisa

from device.data import DataBuffer
from device.dg4202 import DG4202, DG4202DataSource, DG4202Detector, DG4202Mock
from device.edux1002a import EDUX1002A, EDUX1002ADataSource, EDUX1002ADetector

DEFAULT_DICT = {"dg_last_alive": None, "edux_last_alive": None}


class StateManager:
    def __init__(self, json_file: Path = None):
        self.json_file = json_file or Path(os.getenv("DATA"), "state.json")
        self.birthdate = time.time()

    def read_state(self) -> dict:
        try:
            if self.json_file.stat().st_size > 0:
                with open(self.json_file, "r") as f:
                    return json.load(f)
            else:
                return {"dg_last_alive": None}
        except (FileNotFoundError, ValueError):
            return {"dg_last_alive": None}

    def write_state(self, state: dict):
        with open(self.json_file, "w") as f:
            json.dump(state, f)

    def get_uptime(self):
        """
        Function to get uptime from last known device uptime.

        Returns:
            str: Uptime in HH:MM:SS format if known, otherwise 'N/A'.
        """
        uptime_seconds = time.time() - self.birthdate
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        return uptime_str


class DG4202Manager:
    def __init__(
        self,
        state_manager: StateManager,
        args_dict: dict,
        resource_manager: pyvisa.ResourceManager,
    ):
        self.state_manager = state_manager
        self.args_dict = args_dict
        self._mock_device = DG4202Mock()
        self.function_map = self._initialize_function_map()  # required for scheduler
        self.rm = resource_manager
        self.data_source = None
        self._initialize_device()

    def _initialize_device(self):
        if self.args_dict["hardware_mock"]:
            self.dg4202_device = self._mock_device
        else:
            self.dg4202_device = DG4202Detector(
                resource_manager=self.rm
            ).detect_device()

        self.data_source = DG4202DataSource(self.dg4202_device)

    def _output_on_off_wrapper(self, *args, **kwargs):
        if not self.dg4202_device.is_connection_alive():
            # Log the disconnection
            print(f"Device is disconnected at {datetime.now()}")
            return None
        return self.dg4202_device.output_on_off(*args, **kwargs)

    def get_device(self) -> DG4202:
        """
        Function to create a DG4202 device.
        Updates the state depending on the device creation.

        Args:
            args_dict (dict): Dictionary of arguments.

        Returns:
            DG4202: A DG4202 device object.
        """
        state = self.state_manager.read_state()
        if self.args_dict["hardware_mock"]:
            if self._mock_device.killed:
                # Simulate dead device
                state["dg_last_alive"] = None
                self.state_manager.write_state(state)
                self.dg4202_device = None
            else:
                if state["dg_last_alive"] is None:
                    state["dg_last_alive"] = time.time()
                self.state_manager.write_state(state)
                self.dg4202_device = self._mock_device
        else:
            self.dg4202_device = DG4202Detector(
                resource_manager=self.rm
            ).detect_device()
            if self.dg4202_device is None:
                state["dg_last_alive"] = None  # Reset the uptime
            else:
                if state["dg_last_alive"] is None:
                    state["dg_last_alive"] = time.time()
            self.state_manager.write_state(state)
        self.data_source = DG4202DataSource(self.dg4202_device)
        return self.dg4202_device

    def get_device_uptime(self, args_dict: dict):
        """
        Function to get device uptime from last known device uptime.

        Args:
            args_dict (dict): Dictionary of arguments.

        Returns:
            str: Uptime in HH:MM:SS format if known, otherwise 'N/A'.
        """
        state = self.state_manager.read_state()
        if state["dg_last_alive"]:
            uptime_seconds = time.time() - state["dg_last_alive"]
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            return uptime_str
        else:
            return "N/A"


class EDUX1002AManager:
    def __init__(
        self,
        state_manager: StateManager,
        args_dict: dict,
        resource_manager: pyvisa.ResourceManager,
        buffer_size: int,
    ):
        self.state_manager = state_manager
        self.args_dict = args_dict
        self.rm = resource_manager
        self._mock_device = MagicMock()  # TODO: create!
        self.buffers = {1: None, 2: None}
        self.buffer_size = buffer_size
        self._initialize_device()
        self.function_map = self._initialize_function_map()  # required for scheduler

    def _initialize_device(self):
        detector = EDUX1002ADetector(resource_manager=self.rm)
        if self.args_dict["hardware_mock"]:
            self.edux1002a_device = self._mock_device
        else:
            self.edux1002a_device = detector.detect_device()
        if not self.edux1002a_device:
            print("Failed to initialize EDUX1002A device.")
            return
        self.buffers = {
            1: DataBuffer(
                EDUX1002ADataSource(self.edux1002a_device, 1), self.buffer_size
            ),
            2: DataBuffer(
                EDUX1002ADataSource(self.edux1002a_device, 2), self.buffer_size
            ),
        }

    def is_device_alive(self) -> bool:
        try:
            idn = self.edux1002a_device.interface.read("*IDN?")
            return "EDU-X 1002A" in idn
        except Exception as e:
            return False

    def _get_waveform_wrapper(self, *args, **kwargs):
        if not self.is_device_alive():
            # Log the disconnection
            print(f"Device is disconnected at {datetime.now()}")
            return None
        return self.edux1002a_device.get_waveform(*args, **kwargs)

    def get_device(self) -> EDUX1002A:
        """
        Function to create an EDUX1002A device.
        Updates the state depending on the device creation.
        Args:
            args_dict (dict): Dictionary of arguments.
        Returns:
            EDUX1002A: An EDUX1002A device object.
        """
        state = self.state_manager.read_state()
        if self.args_dict["hardware_mock"]:
            if self._mock_device.killed:
                # Simulate dead device
                state["edux_last_alive"] = None
                self.state_manager.write_state(state)
                return None
            else:
                if state["edux_last_alive"] is None:
                    state["edux_last_alive"] = time.time()
                self.state_manager.write_state(state)
                self.edux1002a_device = self._mock_device
                return self.edux1002a_device
        else:
            self.edux1002a_device = EDUX1002ADetector(
                resource_manager=self.rm
            ).detect_device()
            if self.edux1002a_device is None:
                state["edux_last_alive"] = None  # Reset the uptime
            else:
                self.buffers = {
                    1: DataBuffer(
                        EDUX1002ADataSource(self.edux1002a_device, 1), self.buffer_size
                    ),
                    2: DataBuffer(
                        EDUX1002ADataSource(self.edux1002a_device, 2), self.buffer_size
                    ),
                }
                if state["edux_last_alive"] is None:
                    state["edux_last_alive"] = time.time()
            self.state_manager.write_state(state)
            return self.edux1002a_device
