from device.interface import Interface


class Device:
    def __init__(self, interface: Interface):
        self.interface = interface


class MockDevice(Device):
    def __init__(self, interface: Interface):
        super().__init__(interface)
        self.killed = False
