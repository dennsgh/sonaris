import abc

import pyvisa


class Interface(abc.ABC):

    def __init__(self, resource: pyvisa.Resource):
        self.inst = resource

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
