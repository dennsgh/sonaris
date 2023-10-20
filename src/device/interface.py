import abc

import pyvisa
from typing import Optional

from datetime import datetime


class Interface(abc.ABC):

    def __init__(self, resource: pyvisa.Resource, address: Optional[str] = None):
        self.inst = resource
        self.address = address
        self.debug = False

    @abc.abstractmethod
    def write(self, command: str) -> None:
        """
        Abstract method for writing a command to the interface.

        Args:
            command (str): The command to be written.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, command: str) -> str:
        """
        Abstract method for reading a response from the interface.

        Args:
            command (str): The command to be sent for reading.

        Returns:
            str: The response received from the interface.
        """
        raise NotImplementedError


class EthernetInterface(Interface):

    def __init__(self, resource: pyvisa.Resource):
        ip_address = resource.split("::")[0].split("TCPIP")[
            1]  # Extract IP from the resource string
        super().__init__(resource, address=ip_address)

    def write(self, command: str) -> None:
        self.inst.write(command)
        if self.debug:
            print(f"[{datetime.now()}]{command}")

    def read(self, command: str) -> str:
        if self.debug:
            print(f"[{datetime.now()}]{command}")
        return self.inst.query(command)


class USBInterface(Interface):

    def __init__(self, resource: pyvisa.Resource):
        usb_address = resource  # You can further parse the resource string if needed
        super().__init__(resource, address=usb_address)

    def write(self, command: str) -> None:
        self.inst.write(command)
        if self.debug:
            print(f"[{datetime.now()}]{command}")

    def read(self, command: str) -> str:
        if self.debug:
            print(f"[{datetime.now()}]{command}")
        return self.inst.query(command)
