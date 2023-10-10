import pyvisa
from pyvisa.resources import Resource
import re
from typing import Optional
from device.interface import Interface
from collections import deque
import numpy as np

from device.data import DataSource


class EDUX1002ADetector:

    def __init__(self, resource_manager: pyvisa.ResourceManager):
        self.rm = resource_manager

    def detect_device(self) -> Optional['EDUX1002A']:
        resources = self.rm.list_resources()
        for resource in resources:
            if resource.startswith("TCPIP"):
                detected_device = self._detect_via_protocol(resource, EDUX1002AEthernet)
                if detected_device:
                    return detected_device
            elif resource.startswith("USB"):
                detected_device = self._detect_via_protocol(resource, EDUX1002AUSB)
                if detected_device:
                    return detected_device

        return None

    def _detect_via_protocol(self, resource: str, protocol_cls: type) -> Optional['EDUX1002A']:
        try:
            device = self.rm.open_resource(resource)
            idn = device.query("*IDN?")
            if "EDU-X 1002A" in idn:
                if issubclass(protocol_cls, EDUX1002AEthernet):
                    return EDUX1002A(protocol_cls(resource.split('::')[1]))
                return EDUX1002A(protocol_cls(resource))
        except pyvisa.errors.VisaIOError as e:
            print(f"Failed to connect with resource {resource}. Error: {e}")
        return None


class EDUX1002AEthernet(Interface):

    def __init__(self, ip_address: str):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(f'TCPIP::{ip_address}::INSTR')

    def write(self, command: str) -> None:
        self.inst.write(command)

    def read(self, command: str) -> str:
        return self.inst.query(command)


class EDUX1002AUSB(Interface):

    def __init__(self, resource_name: str):
        rm = pyvisa.ResourceManager()
        self.inst: Resource = rm.open_resource(resource_name)

    def write(self, command: str) -> None:
        self.inst.write(command)

    def read(self, command: str) -> str:
        return self.inst.query(command)


class EDUX1002A:
    """Keysight EDUX1002A hardware driver/wrapper."""

    def __init__(self, interface, buffer_size: int = 512, timeout=20000):
        self.buffer = deque(maxlen=buffer_size)
        self.interface = interface
        self.interface.inst.timeout = timeout

    def setup_waveform_readout(self, channel: int = 1):
        """Setup the oscilloscope for waveform readout."""
        self.interface.write(f"CHANNEL{channel}:DISPLAY ON")
        self.interface.write(f"DATA:SOURCE CHANNEL{channel}")
        self.interface.write("WAVEFORM:FORMAT ASCII")

    def get_waveform_preamble(self):
        """Retrieve the waveform preamble which provides data on the waveform format."""
        preamble = self.interface.read("WAVeform:PREamble?")
        return [float(val) for val in preamble.split(',')]

    def get_waveform_data(self):
        """Get the waveform data from the oscilloscope."""
        waveform_data = self.interface.read("WAVeform:DATA?")

        # Check for header
        if waveform_data[0] == '#':
            num_digits = int(waveform_data[1])
            num_data_points = int(waveform_data[2:2 + num_digits])

            # Extract the actual data without the header
            waveform_data = waveform_data[2 + num_digits:]

        return np.array([float(val) for val in waveform_data.split(',')])

    def get_waveform(self, channel: int = 1):
        """Public method to setup, retrieve, and process waveform data."""
        self.setup_waveform_readout(channel)
        preamble = self.get_waveform_preamble()
        waveform_data = self.get_waveform_data()

        # Extract information from preamble
        x_increment = preamble[4]
        x_origin = preamble[5]
        y_increment = preamble[7]
        y_origin = preamble[8]

        # Convert data to actual voltage and time values
        time = np.arange(len(waveform_data)) * x_increment + x_origin
        voltage = waveform_data * y_increment + y_origin

        return time, voltage

    def update_buffer(self, channel: int = 1):
        _, voltage = self.get_waveform(channel)
        self.buffer.append(voltage)

    def set_timeout(self, timeout):
        self.interface.inst.timeout = timeout


class EDUX1002ADataSource(DataSource):

    def __init__(self, device: EDUX1002A, channel: int = 1):
        super().__init__(device)
        self.channel = channel

    def query_data(self):
        try:
            time, voltage = self.device.get_waveform(self.channel)
            return voltage
        except:
            return []
