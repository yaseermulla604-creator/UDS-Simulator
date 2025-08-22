from .can_tp import CAN_TP
from .event_manager import EventManager
from .UDSException import UDSException
from .frame import Frame
from .uds_sid_19 import Ox19
from .uds_sid_22 import Ox22
from .uds_sid_2E import Ox2E
import queue
import threading
import time

class UDS:
    START_SESSION = (0x10, 0x03)

    def __init__(self, interface, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager):
        self.interface = interface
        self.tx_id = tx_id
        self.rx_id = rx_id
        self.channel = channel
        self.baud_rate = baud_rate
        self.message_type = message_type
        self.event_manager = event_manager
        self.can_tp = CAN_TP(interface, tx_id, channel, baud_rate, message_type, event_manager)
        self.event_manager.publish('rx_id', rx_id)
        self.event_manager.subscribe('data_to_uds', self.process_response)
        self._buffer_to_cantp = queue.Queue()
        self._sid_output_display = queue.Queue()
        self._output_terminal = queue.Queue()
        self.frame = Frame()
        self.handlers = {
            0x19: Ox19(self),
            0x22: Ox22(self),
            0x2E: Ox2E(self)
        }
        self.p2_timer = 0.05
        self.p2_star_timer = 5
        self.waiting_for_response = False
        self.response_pending = False
        self.current_request = None
        self.session_started = False
        self.request_lock = threading.Lock()
        self._immediate_request_queue = queue.Queue()

    def update_interface(self, interface, tx_id, rx_id, channel, baud_rate, message_type):
        self.interface = interface
        self.tx_id = tx_id
        self.rx_id = rx_id
        self.channel = channel
        self.baud_rate = baud_rate
        self.message_type = message_type
        self.can_tp.update_interface(interface, tx_id, channel, baud_rate, message_type)

    def start_session(self):
        if not self.session_started:
            print("Starting diagnostic session")
            self.send_request(self.START_SESSION, immediate=True)
            self.session_started = True

    def send_request(self, data, immediate=False):
        self.received_data = data
        self._output_terminal.put(self.received_data)
        with self.request_lock:
            if immediate:
                self._immediate_request_queue.put(self.received_data)
                self.process_immediate_request()
            elif not self.session_started and self.received_data != self.START_SESSION:
                print("Queueing request.")
                self._buffer_to_cantp.put(self.received_data)
            elif self.waiting_for_response:
                print("Waiting for response, queueing new request")
                self._buffer_to_cantp.put(self.received_data)
            else:
                self.prepare_and_send_request(self.received_data)

    def process_immediate_request(self):
        while not self._immediate_request_queue.empty():
            data = self._immediate_request_queue.get()
            print(f"Sending immediate request: {data}")
            self.can_tp.receive_data_from_uds(data)

    def prepare_and_send_request(self, data):
        self.current_request = data
        self.waiting_for_response = True
        self.response_pending = False
        print(f"Sending request: {data}")
        self.can_tp.receive_data_from_uds(data)
        threading.Thread(target=self.response_timeout_handler).start()

    def process_request_queue(self):
        with self.request_lock:
            self.process_immediate_request()
            if not self.waiting_for_response and not self._buffer_to_cantp.empty():
                request = self._buffer_to_cantp.get()
                self.prepare_and_send_request(request)

    def process_response(self, response):
        self.received_response = response
        self._output_terminal.put(self.received_response)
        try:
            print("process_response", self.received_response)
            if self.received_response[0] == '0x7F':
                if self.received_response[2] == '0x78':
                    print("Received ResponsePending (0x78)")
                    self.response_pending = True
                    threading.Thread(target=self.wait_for_response).start()
                else:
                    self.handle_response(self.received_response)
            else:
                self.handle_response(self.received_response)
        except Exception as e:
            print(f"Unexpected Error: {e}")

    def handle_response(self, response):
        with self.request_lock:
            print("handle response")
            self.waiting_for_response = False
            self.response_pending = False
            if response[0] == '0x50':
                print("received session positive response")
                self.update_timers(response)
                print("Diagnostic session started successfully")
                self.session_started = True
                self.process_queued_requests()
            elif response[0] == '0x7E':
                print("received session positive response")
                self.update_timers(response)
                print("Tester Present")
                self.session_started = True
                self.process_queued_requests()
            elif response[0] == '0x7F':
                print("Negative Response Detected:", response)
                nrc = response[2]
                print("NRC:", nrc)
                if self.current_request == self.START_SESSION:
                    self.session_started = False
                print(UDSException.create_exception(nrc))
            else:
                self.direct_to_sid(response)
                self.process_request_queue()
    def update_timers(self, response):
        print("UPDATE TIMERS")
        if len(response) >= 4:
            self.p2_timer = (int(response[2], 16) << 8 | int(response[3], 16)) / 1000
        if len(response) >= 6:
            self.p2_star_timer = (int(response[4], 16) << 8 | int(response[5], 16)) / 1000
        print(f"Updated timers - P2: {self.p2_timer}s, P2*: {self.p2_star_timer}s")

    def wait_for_response(self):
        timeout = self.p2_star_timer
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.response_pending:
                return
            time.sleep(0.01)
        print(f"Timeout occurred while waiting for response after 0x78")
        self.waiting_for_response = False
        self.response_pending = False
        self.process_request_queue()

    def response_timeout_handler(self):
        timeout = self.p2_timer if self.current_request != self.START_SESSION else self.p2_star_timer
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.waiting_for_response or self.response_pending:
                return
            time.sleep(0.1)
        if self.waiting_for_response and not self.response_pending:
            print(f"Timeout occurred while waiting for response to {self.current_request}")
            self.waiting_for_response = False
            if self.current_request == self.START_SESSION:
                self.session_started = False

    def direct_to_sid(self, response):
        self.Frame_response = response
        print("direct_to_sid", self.Frame_response)
        self.sid = self.frame.get_sid(self.Frame_response)
        print("sid received: ", self.sid)

        # Check if the SID is 0x62 (Tester Present) and ignore it
        if self.sid == 0x62:
            print("Ignoring Tester Present response (SID 0x62)")
            self.process_request_queue()  # Continue processing the request queue
            return

        handler = self.handlers.get(self.sid)
        if handler:
            handler.buffer_frame(self.Frame_response)
        else:
            print(f"No handler for SID {self.sid}")

    def process_next_request(self):
        if not self.waiting_for_response and not self._buffer_to_cantp.empty():
            request = self._buffer_to_cantp.get()
            print(f"Sending request: {request}")
            self.can_tp.receive_data_from_uds(request)
            self.waiting_for_response = True
            self.response_pending = False
            threading.Thread(target=self.response_timeout_handler).start()
        
    def added_from_sid(self, data):
        self.event_manager.publish('response_received', data)
        self._sid_output_display.put(data)

    def process_queued_requests(self):
        while not self._buffer_to_cantp.empty():
            with self.request_lock:
                if not self.waiting_for_response:
                    request = self._buffer_to_cantp.get()
                    self.prepare_and_send_request(request)
                else:
                    break  # Stop processing if waiting for a response
            while self.waiting_for_response:
                time.sleep(0.01)