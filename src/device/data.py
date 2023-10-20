from collections import deque
import numpy as np
import abc


class DataSource(abc.ABC):

    def __init__(self, device: abc.ABC):
        self.device: abc.ABC = device
        pass

    def query_data(self):
        raise NotImplementedError


class DataBuffer:

    def __init__(self, data_source: DataSource, buffer_size: int = 128):
        self.buffer = deque(maxlen=buffer_size)
        self.data_source = data_source
        self.buffer_size = buffer_size

    def update(self):
        new_data = self.data_source.query_data()
        self.buffer.append(new_data)

    def get_data(self):
        return np.concatenate(list(self.buffer))
