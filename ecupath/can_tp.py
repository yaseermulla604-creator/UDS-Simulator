from .Can import CAN
from .event_manager import EventManager
from .frame import Frame
import queue
import threading

class CAN_TP:
    def __init__(self, interface, tx_id, channel, baud_rate, message_type, event_manager: EventManager) -> None:
        self.event_manager = event_manager
        self.interface = interface
        self.can = CAN(interface, tx_id, channel, baud_rate, message_type, event_manager)
        self.event_manager.subscribe('data_received', self.get_data)
        self.store_data = []
        self._buffer_to_can = queue.Queue()
        self._buffer_from_uds = queue.Queue()
        self.frame = Frame()
        self.bytes = None
        self.no_of_frames = 0
        self.frames_received = 0
        self.counter = 0
        self.block_size = 4
        self.time_between_consecutive_frames = 20
        self.remaining_data = None
        self.sequence_number = 1
        self.transmission_lock = threading.Lock()

    def update_interface(self, interface, tx_id, channel, baud_rate, message_type):
        self.interface = interface
        self.can.update_interface(interface, tx_id, channel, baud_rate, message_type)

    def get_data(self, incoming_frame):
        self.process_frame(incoming_frame)

    def send_data(self, data):
        print("send_data:", data)
        with self.transmission_lock:
            self.can.transmit_data(data)

    def process_frame(self, incoming_frame):
        if all(byte == 0 for byte in incoming_frame):
            print("Ignoring frame with all zeros")
            return
        self.frame_type = self.frame.validate_frame(incoming_frame)
        if self.frame_type == self.frame.SINGLE_FRAME:
            self.store_data = []
            self.temp = list(incoming_frame[1:])
            self.store_data.extend(self.temp)
            print("Sending data from single frame")
            self.route_frame()
        elif self.frame_type == self.frame.FIRST_FRAME:
            self.bytes = self.frame.extract_length(incoming_frame)
            self.no_of_frames = (self.bytes + 6) // 7
            self.frames_received = 0
            self.counter = min(self.no_of_frames, self.block_size)
            self.store_data = list(incoming_frame[2:])
            self.FC_frame = self.frame.construct_flow_control(self.counter, self.time_between_consecutive_frames)
            self.send_data(self.FC_frame)
            print(f"First frame received. Expecting {self.no_of_frames} more frames.")
        elif self.frame_type == self.frame.CONSECUTIVE_FRAME:
            self.frames_received += 1
            self.counter -= 1
            self.temp = list(incoming_frame[1:])
            self.store_data.extend(self.temp)
            print(f"Consecutive frame received. Total frames received: {self.frames_received}/{self.no_of_frames}")
            if self.frames_received == self.no_of_frames:
                print("All frames received. Sending data from consecutive frames.")
                self.route_frame()
            elif self.counter == 0:
                if self.frames_received < self.no_of_frames:
                    self.counter = min(self.no_of_frames - self.frames_received, self.block_size)
                    self.FC_frame = self.frame.construct_flow_control(self.counter, self.time_between_consecutive_frames)
                    self.send_data(self.FC_frame)
                    print(f"Sent Flow Control frame, expecting {self.counter} more frames")
        elif self.frame_type == self.frame.FLOW_CONTROL_FRAME:
            self.rec_block_size = incoming_frame[1]
            self.time_between_consecutive_frames = incoming_frame[2]
            print(f"Flow control frame received: block size = {self.rec_block_size}, time between frames = {self.time_between_consecutive_frames} ms")
            self.send_consecutive_frames(self.rec_block_size)

    def route_frame(self):
        self.store_data = self.frame.hex(self.store_data)
        self.store_data = tuple(self.store_data)
        print("Publishing data to uds")
        self.event_manager.publish('data_to_uds', self.store_data)
        self.store_data = []

    def process_uds_data(self, data):
        print(data)
        if len(data) <= 7:
            frame = ([len(data)])
            frame.extend(data)
            frame.extend([0] * (8 - len(frame)))
            frame_tuple = tuple(frame)
            print("buffer_to_can: ", frame_tuple)
            self._buffer_to_can.put(frame_tuple)
        else:
            self.send_multi_frame(data)

    def send_multi_frame(self, data):
        total_length = len(data)
        first_frame = ([0x10 | (total_length >> 8), total_length & 0xFF])
        first_frame.extend(data[:6])
        first_frame_tuple = tuple(first_frame)
        self._buffer_to_can.put(first_frame_tuple)
        self.remaining_data = data[6:]
        self.sequence_number = 1

    def send_consecutive_frames(self, received_block_size):
        self.received_block_size = received_block_size
        if not self.remaining_data:
            return
        for _ in range(self.received_block_size):
            if not self.remaining_data:
                break
            frame = ([0x20 | (self.sequence_number & 0x0F)])
            frame.extend(self.remaining_data[:7])
            self.remaining_data = self.remaining_data[7:]
            if len(frame) < 8:
                frame.extend([0xAA] * (8 - len(frame)))
            frame_tuple = tuple(frame)
            self._buffer_to_can.put(frame_tuple)
            self.sequence_number = (self.sequence_number + 1) & 0x0F
        if not self.remaining_data and self.received_block_size > 0:
            print("No more data to send. Sending 'AA' as padding data.")
            while self.received_block_size > 0:
                frame = ([0x20 | (self.sequence_number & 0x0F)])
                frame.extend([0xAA] * 7)
                frame_tuple = tuple(frame)
                self._buffer_to_can.put(frame_tuple)
                self.sequence_number = (self.sequence_number + 1) & 0x0F
                self.received_block_size -= 1
        self.received_block_size = 0

    def send_data_to_can(self):
        while not self._buffer_to_can.empty():
            self.frame_to_can = self._buffer_to_can.get()
            print("sending data to can: ", self.frame_to_can)
            self.send_data(self.frame_to_can)

    def receive_data_from_uds(self, data):
        print("Data received from uds: ", data)
        self._buffer_from_uds.put(data)

    def process_uds_queue(self):
        while not self._buffer_from_uds.empty():
            data = self._buffer_from_uds.get()
            print("process uds data: ", data)
            self.process_uds_data(data)

    def cantp_monitor(self):
        self.process_uds_queue()
        self.send_data_to_can()