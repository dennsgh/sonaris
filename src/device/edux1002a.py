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

    def _detect_via_protocol(self, resource_name: str, protocol_cls: type) -> Optional['EDUX1002A']:
        try:
            device = self.rm.open_resource(resource_name)
            idn = device.query("*IDN?")
            if "EDU-X 1002A" in idn:
                return protocol_cls(device)
        except pyvisa.errors.VisaIOError as e:
            print(f"Failed to connect with resource {resource_name}. Error: {e}")
        return None


class EDUX1002AEthernet(Interface):

    def __init__(self, resource: Resource):
        super().__init__(resource)

    def write(self, command: str) -> None:
        self.inst.write(command)

    def read(self, command: str) -> str:
        return self.inst.query(command)


class EDUX1002AUSB(Interface):

    def __init__(self, resource: Resource):
        super().__init__(resource)

    def write(self, command: str) -> None:
        self.inst.write(command)

    def read(self, command: str) -> str:
        return self.inst.query(command)


class EDUX1002A:
    """Keysight EDUX1002A hardware driver/wrapper."""

    def __init__(self, interface: Interface, timeout=20000):
        self.interface = interface
        self.interface.inst.timeout = timeout

    def initialize(self):
        """Reset and clear the oscilloscope to default settings."""
        self.interface.write("*RST")
        self.interface.write("*CLS")

    def autoscale(self):
        """Use Autoscale for automatic oscilloscope setup."""
        self.interface.write(":AUToscale")

    def set_trigger_mode(self, mode="EDGE"):
        """Set the trigger mode of the oscilloscope."""
        self.interface.write(f":TRIGger:MODE {mode}")

    def digitize(self, channel=1):
        """Capture data using the :DIGitize command."""
        self.interface.write(f":DIGitize CHANnel{channel}")

    def query_oscilloscope(self, query):
        """Read query responses from the oscilloscope."""
        return self.interface.read(query)

    def check_instrument_status(self):
        """Check and print the instrument's status."""
        status = self.interface.read(":SYSTem:ERRor?")
        print(f"Oscilloscope Status: {status}")
        return status

    def set_acquisition_mode(self, mode="RTIMe"):
        """
        Set the acquisition mode of the oscilloscope.
        
        Parameters:
        - mode (str): The acquisition mode to set. Options are "RTIMe" for real-time mode
                      and "SEGMented" for segmented mode. Default is "RTIMe".
        """
        if mode not in ["RTIMe", "SEGMented"]:
            raise ValueError("Invalid acquisition mode. Choose 'RTIMe' or 'SEGMented'.")

        self.interface.write(f":ACQuire:MODE {mode}")

    def is_real_time_mode(self):
        """Check if the oscilloscope is in real-time mode."""
        current_mode = self.interface.read(":ACQuire:MODE?")
        return current_mode.strip() == "RTIMe"

    def setup_waveform_readout(self, channel: int = 1):
        """Setup the oscilloscope for waveform readout."""
        self.interface.write(f"CHANNEL{channel}:DISPLAY ON")
        #self.interface.write(f"DATA:SOURCE CHANNEL{channel}")
        self.interface.write("WAVeform:FORMat ASCII")
        self.interface.write(f"WAVeform:SOURce CHANnel{channel}")

    def get_waveform_preamble(self):
        """Retrieve the waveform preamble which provides data on the waveform format."""
        preamble = self.interface.read("WAVeform:PREamble?")
        return [float(val) for val in preamble.split(',')]

    def get_waveform_data(self, channel: int = 1):
        """Get the waveform data from the oscilloscope."""
        self.setup_waveform_readout(channel)
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

    def set_timeout(self, timeout):
        self.interface.inst.timeout = timeout

    def set_acquisition_type(self, acq_type="NORMal"):
        """
        Set the data acquisition type of the oscilloscope.

        Parameters:
        - acq_type (str): The acquisition type to set. Options are "NORMal", "AVERage", 
                          "HRESolution", and "PEAK". Default is "NORMal".
        """
        valid_types = ["NORMal", "AVERage", "HRESolution", "PEAK"]
        if acq_type not in valid_types:
            raise ValueError(f"Invalid acquisition type. Choose one of {valid_types}.")

        self.interface.write(f":ACQuire:TYPE {acq_type}")

    def get_acquisition_type(self):
        """
        Query the oscilloscope for the current acquisition type.
        
        Returns:
        - str: The current acquisition type. One of "NORM", "AVER", "HRES", or "PEAK".
        """
        return self.interface.read(":ACQuire:TYPE?").strip()

    def set_acquisition_count(self, count=1):
        """
        Set the acquisition count. Relevant only for "AVERage" acquisition type.

        Parameters:
        - count (int): The number of averages. An integer from 1 to 65536.
        """
        if not 1 <= count <= 65536:
            raise ValueError("Acquisition count should be an integer between 1 and 65536.")

        self.interface.write(f":ACQuire:COUNt {count}")


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
