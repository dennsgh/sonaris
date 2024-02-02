import abc
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pyvisa

# Import classes and modules from device module as needed.
from device.data import DataBuffer
from device.dg4202 import DG4202, DG4202DataSource, DG4202Detector, DG4202Mock
from device.edux1002a import (
    EDUX1002A,
    EDUX1002ADataSource,
    EDUX1002ADetector,
    EDUX1002AMock,
)

# Setting up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class StateManager:
    def __init__(self, json_file: Path = None):
        self.json_file = json_file or Path(os.getenv("DATA"), "state.json")
        self.birthdate = time.time()

    def read_state(self) -> dict:
        try:
            with open(self.json_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error("State file not found, returning default state.")
            return self.default_state()
        except json.JSONDecodeError:
            logging.error("Invalid JSON format in state file, returning default state.")
            return self.default_state()

    def write_state(self, state: dict):
        existing_state = self.read_state()
        existing_state.update(state)
        with open(self.json_file, "w") as f:
            json.dump(existing_state, f)

    def default_state(self):
        return {}

    def update_device_last_alive(self, device_type: str, last_alive_time=None):
        state = self.read_state()
        key = f"{device_type}_last_alive"
        state[key] = last_alive_time or time.time()
        self.write_state(state)

    def get_device_last_alive(self, device_type: str):
        state = self.read_state()
        return state.get(f"{device_type}_last_alive")

    def get_uptime(self) -> str:
        uptime_seconds = time.time() - self.birthdate
        return str(timedelta(seconds=int(uptime_seconds)))


class DeviceManagerBase(abc.ABC):
    device_type = "managed_device"

    def __init__(
        self,
        state_manager: StateManager,
        args_dict: dict,
        resource_manager: pyvisa.ResourceManager,
    ):
        self.state_manager = state_manager
        self.args_dict = args_dict
        self.rm = resource_manager

    def is_device_alive(self) -> bool:
        raise NotImplementedError("Must be implemented in subclasses.")

    def get_device(self):
        raise NotImplementedError("Must be implemented in subclasses.")

    def update_device_state(self):
        alive = self.is_device_alive()
        if alive:
            self.state_manager.update_device_last_alive(self.device_type, time.time())
        else:
            self.state_manager.update_device_last_alive(self.device_type, None)

    def get_device_uptime(self) -> str:
        last_alive = self.state_manager.get_device_last_alive(self.device_type)
        if last_alive:
            uptime_seconds = time.time() - last_alive
            return str(timedelta(seconds=int(uptime_seconds)))
        else:
            return "N/A"


class DG4202Manager(DeviceManagerBase):
    device_type = "dg"

    def __init__(
        self,
        state_manager: StateManager,
        args_dict: dict,
        resource_manager: pyvisa.ResourceManager,
    ):
        super().__init__(state_manager, args_dict, resource_manager)
        self._mock_device = DG4202Mock()
        self.data_source = None
        self.dg4202_device = None
        self._initialize_device()

    def _initialize_device(self):
        if self.args_dict["hardware_mock"]:
            self.dg4202_device = self._mock_device
        else:
            self.dg4202_device = DG4202Detector(
                resource_manager=self.rm
            ).detect_device()

        self.data_source = DG4202DataSource(self.dg4202_device)

    def get_device(self) -> DG4202:
        state = self.state_manager.read_state()
        if self.args_dict["hardware_mock"]:
            if self._mock_device.killed:
                state["dg_last_alive"] = None
                self.state_manager.write_state(state)
                self.dg4202_device = None
            else:
                if state.get("dg_last_alive") is None:
                    state["dg_last_alive"] = time.time()
                self.state_manager.write_state(state)
                self.dg4202_device = self._mock_device
        else:
            self.dg4202_device = DG4202Detector(
                resource_manager=self.rm
            ).detect_device()
            if self.dg4202_device is None:
                state["dg_last_alive"] = None
            else:
                if state.get("dg_last_alive") is None:
                    state["dg_last_alive"] = time.time()
            self.state_manager.write_state(state)
        self.data_source = DG4202DataSource(self.dg4202_device)
        return self.dg4202_device

    def is_device_alive(self) -> bool:
        try:
            if self.args_dict["hardware_mock"]:
                return ~self.dg4202_device.killed
            idn = self.dg4202_device.interface.read("*IDN?")
            return "DG4202" in idn
        except Exception as e:
            return False

    def get_data(self) -> dict:
        return self.data_source.query_data() or {}


class EDUX1002AManager(DeviceManagerBase):
    device_type = "edux"

    def __init__(
        self,
        state_manager: StateManager,
        args_dict: dict,
        resource_manager: pyvisa.ResourceManager,
        buffer_size: int,
    ):
        super().__init__(state_manager, args_dict, resource_manager)
        self._mock_device = EDUX1002AMock()
        self.buffers = {1: None, 2: None}
        self.buffer_size = buffer_size
        self._initialize_device()

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

    def get_device(self) -> EDUX1002A:
        state = self.state_manager.read_state()
        if self.args_dict["hardware_mock"]:
            if self._mock_device.killed:
                state["edux_last_alive"] = None
                self.state_manager.write_state(state)
                self.edux1002a_device = None
            else:
                if state.get("edux_last_alive") is None:
                    state["edux_last_alive"] = time.time()
                self.state_manager.write_state(state)
                self.edux1002a_device = self._mock_device
        else:
            self.edux1002a_device = EDUX1002ADetector(
                resource_manager=self.rm
            ).detect_device()
            if self.edux1002a_device is None:
                state["edux_last_alive"] = None
            else:
                if state.get("edux_last_alive") is None:
                    state["edux_last_alive"] = time.time()
            self.state_manager.write_state(state)
        self.data_source = EDUX1002ADataSource(self.edux1002a_device)
        return self.edux1002a_device

    def autoscale(self, *args, **kwargs):
        self.edux1002a_device.autoscale()

    def is_device_alive(self) -> bool:
        try:
            if self.args_dict["hardware_mock"]:
                return ~self.edux1002a_device.killed
            idn = self.edux1002a_device.interface.read("*IDN?")
            return "EDU-X 1002A" in idn
        except Exception as e:
            return False

    def get_data(self) -> dict:
        return {1: self.buffers[1].get_data(), 2: self.buffers[2].get_data()}
