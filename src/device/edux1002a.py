import re
from typing import Optional

import numpy as np
import pyvisa

from device.data import DataSource
from device.interface import EthernetInterface, Interface, USBInterface


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

    def set_acquisition_complete(self, percentage: int):
        """
        Set the percent completion for the acquisition process.

        Parameters:
        - percentage (int): Percentage of completion. An integer between 0 and 100.
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage should be an integer between 0 and 100.")

        self.interface.write(f":ACQuire:COMPlete {percentage}")

    def set_waveform_source(self, channel: int = 1):
        """
        Set the waveform source.

        Parameters:
        - channel (int): The channel to set as the waveform source.
        """
        self.interface.write(f":WAVeform:SOURce CHANnel{channel}")

    def set_waveform_format(self, format: str):
        """
        Set the waveform data format.

        Parameters:
        - format (str): The format for the waveform data. Options include "BYTE", "WORD", and "ASCII".
        """
        valid_formats = ["BYTE", "WORD", "ASCII"]
        if format not in valid_formats:
            raise ValueError(f"Invalid format. Choose one of {valid_formats}.")

        self.interface.write(f":WAVeform:FORMat {format}")

    def set_waveform_points(self, points: int):
        """
        Set the number of waveform points to retrieve.

        Parameters:
        - points (int): The number of points to retrieve.
        """
        self.interface.write(f":WAVeform:POINts {points}")

    def get_waveform_data_raw(self):
        """
        Get the raw waveform data from the oscilloscope.

        Returns:
        - str: The raw waveform data.
        """
        return self.interface.read(":WAVeform:DATA?")

    def set_trigger_mode(self, mode="EDGE"):
        """Set the trigger mode of the oscilloscope."""
        self.interface.write(f":TRIGger:MODE {mode}")

    def digitize(self, channel=0):
        """Capture data using the :DIGitize command."""
        if channel == 0:
            self.interface.write(":DIGitize")
        else:
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

    def setup_waveform_readout(self, channel: int = 1, mode="ASCII"):
        """Setup the oscilloscope for waveform readout."""
        # self.interface.write(f"CHANNEL{channel}:DISPLAY ON")
        # self.interface.write(f"DATA:SOURCE CHANNEL{channel}")
        # self.set_waveform_format(mode)
        self.set_waveform_source(channel)

    def get_waveform_preamble(self):
        """Retrieve the waveform preamble which provides data on the waveform format."""
        preamble_str = self.interface.read(":WAVeform:PREamble?")
        preamble_values = preamble_str.split(",")
        # print(preamble_str)
        # Convert the values according to the documentation
        preamble = [
            int(preamble_values[0]),  # format
            int(preamble_values[1]),  # type
            int(preamble_values[2]),  # points
            int(preamble_values[3]),  # count
            float(preamble_values[4]),  # xincrement
            float(preamble_values[5]),  # xorigin
            int(preamble_values[6]),  # xreference
            float(preamble_values[7]),  # yincrement
            float(preamble_values[8]),  # yorigin
            int(preamble_values[9]),  # yreference
        ]

        return preamble

    def display_preamble_details(self, preamble):
        """Displays the preamble details in a human-readable format."""

        # Expected names and their explanations based on documentation
        names = [
            "Format",
            "Type",
            "Points",
            "Count",
            "X Increment",
            "X Origin",
            "X Reference",
            "Y Increment",
            "Y Origin",
            "Y Reference",
        ]

        format_explanations = {0: "BYTE format", 1: "WORD format", 4: "ASCII format"}

        type_explanations = {
            0: "NORMal type",
            1: "PEAK detect type",
            2: "AVERage type",
        }

        # Extracting the values
        details = [
            format_explanations.get(preamble[0], f"Unknown Value {preamble[0]}"),
            type_explanations.get(preamble[1], f"Unknown Value {preamble[1]}"),
        ] + preamble[2:]

        # Displaying the details
        result_str = "Preamble Details:\n"
        for name, detail in zip(names, details):
            result_str += f"{name}: {detail}\n"

        print(result_str)

    def get_waveform_data(self, channel: int = 1):
        """Get the waveform data from the oscilloscope."""
        self.setup_waveform_readout(channel)
        waveform_data = self.get_waveform_data_raw()
        preamble = self.get_waveform_preamble()

        # Check for header
        if waveform_data[0] == "#":
            num_digits = int(waveform_data[1])
            num_data_points = int(waveform_data[2 : 2 + num_digits])

            # Extract the actual data without the header
            waveform_data = waveform_data[2 + num_digits :]

        format_type = preamble[0]
        print(self.display_preamble_details(preamble))
        if format_type == 4:  # ASCII
            return preamble, np.array([float(val) for val in waveform_data.split(",")])
        elif format_type == 0:  # BYTE
            return preamble, np.frombuffer(
                waveform_data.encode("latin-1"), dtype=np.int8
            )
        elif format_type == 1:  # WORD
            return preamble, np.frombuffer(
                waveform_data.encode("latin-1"), dtype=np.int16
            )
        else:
            raise ValueError("Unknown waveform format.")

    def get_waveform(self, channel: int = 1):
        """Public method to setup, retrieve, and process waveform data."""
        self.digitize(channel)
        preamble, waveform_data = self.get_waveform_data(channel)

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

    def set_waveform_return_type(self, ret_type="NORMal"):
        """
        Set the data acquisition type of the oscilloscope.

        Parameters:
        - ret_type (str): The acquisition type to set. Options are "NORMal", "AVERage",
                          "HRESolution", and "PEAK". Default is "NORMal".
        """
        valid_types = ["NORMal", "PEAK", "AVERage", "HREsolution"]
        if ret_type not in valid_types:
            raise ValueError(f"Invalid acquisition type. Choose one of {valid_types}.")

        self.interface.write(f":WAVeform:TYPE {ret_type}")

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
            raise ValueError(
                "Acquisition count should be an integer between 1 and 65536."
            )

        self.interface.write(f":ACQuire:COUNt {count}")


class EDUX1002ADetector:
    def __init__(self, resource_manager: pyvisa.ResourceManager):
        self.rm = resource_manager

    def detect_device(self) -> Optional[EDUX1002A]:
        """
        Method that attempts to detect a EDUX1002A device connected via TCP/IP or USB.
        Loops through all available resources, attempting to open each one and query its identity.
        If a EDUX1002A device is found, it creates and returns a DG4202 instance.

        Returns:
            EDUX1002A: An instance of the EDUX1002A class connected to the detected device,
                    or None if no such device is found.
        """
        resources = self.rm.list_resources()

        for resource in resources:
            if re.match("^TCPIP", resource):
                try:
                    device = self.rm.open_resource(resource)
                    idn = device.query("*IDN?")
                    if "EDU-X 1002A" in idn:
                        return EDUX1002A(EthernetInterface(device))
                except pyvisa.errors.VisaIOError:
                    pass
            elif re.match("^USB", resource):
                try:
                    device = self.rm.open_resource(resource)
                    idn = device.query("*IDN?")
                    if "EDU-X 1002A" in idn:
                        return EDUX1002A(USBInterface(device))
                except pyvisa.errors.VisaIOError:
                    pass

        return None


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
