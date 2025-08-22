import queue
from . import Colors
from .frame import Frame

class Ox22:

    def __init__(self, uds_instance):
        self._buffer = queue.Queue()
        self.uds = uds_instance
        self.frame = Frame()
        

    def buffer_frame(self, frame):
        self._buffer.put(frame)
        self.main()

    def main(self):
        if not self._buffer.empty():
            print("I'm in Ox22")
            self.data = self._buffer.get()
            self.uds.added_from_sid(self.data)