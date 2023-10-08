import pyvisa
from pyvisa.resources import Resource
import re
from typing import Optional
from device.interface import Interface


class EDUX1002ADetector:

    @staticmethod
    def detect_device() -> Optional['EDUX1002A']:
        """
        Static method that attempts to detect an EDUX1002A device connected via TCP/IP or USB.
        Loops through all available resources, attempting to open each one and query its identity.
        If an EDUX1002A device is found, it creates and returns an EDUX1002A instance.

        Returns:
            EDUX1002A: An instance of the EDUX1002A class connected to the detected device, 
                       or None if no such device is found.
        """
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        for resource in resources:
            if re.match("^TCPIP", resource):
                try:
                    device = rm.open_resource(resource)
                    idn = device.query("*IDN?")
                    if "EDUX1002A" in idn:
                        return EDUX1002A(EDUX1002AEthernet(resource.split('::')[1]))
                except pyvisa.errors.VisaIOError:
                    pass
            elif re.match("^USB", resource):
                try:
                    device = rm.open_resource(resource)
                    idn = device.query("*IDN?")
                    if "EDUX1002A" in idn:
                        return EDUX1002A(EDUX1002AUSB(resource))
                except pyvisa.errors.VisaIOError:
                    pass

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

    def __init__(self, interface: Interface):
        self.interface = interface

    def setup_waveform_readout(self, channel: int = 1):
        """Setup the oscilloscope for waveform readout"""
        self.interface.write(f"CHANNEL{channel}:DISPLAY ON")
        self.interface.write(f"DATA:SOURCE CHANNEL{channel}")
        self.interface.write("DATA:WIDTH 2")
        self.interface.write("DATA:ENCODING RIBINARY")

    def get_waveform_preamble(self):
        """Retrieve the waveform preamble which provides data on the waveform format"""
        preamble = self.interface.read("WAVEFORM:PREABLE?")
        # Parsing preamble and converting to useful data might be needed here.
        # For simplicity, we'll return it as-is.
        return preamble

    def get_waveform_data(self):
        """Get the waveform data from the oscilloscope"""
        raw_data = self.interface.read("FETCH:WAVEFORM?")
        # You'd need to convert the raw_data to actual waveform values.
        # This might involve considering the data width, encoding, etc.
        # For this example, we'll assume the raw_data is directly usable:
        return raw_data

    def get_waveform(self, channel: int = 1):
        """Public method to setup, retrieve and process waveform data"""
        self.setup_waveform_readout(channel)
        preamble = self.get_waveform_preamble()
        waveform_data = self.get_waveform_data()
        # Here you can process waveform_data further based on the preamble.
        # For simplicity, we'll return the waveform_data as-is.
        return waveform_data
