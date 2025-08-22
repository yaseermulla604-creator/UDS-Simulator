from . import Colors
from .frame import Frame
from .event_manager import EventManager
from .Interface import get_hardware_interface
import queue

class Tx:
    current_instance = None  # Class-level reference to the current instance

    def __init__(self, hardware_interface, tx_id, event_manager):
        self.hardware_interface = hardware_interface
        self.tx_id = tx_id
        self.event_manager = event_manager
        print(self.tx_id, "txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        if Tx.current_instance:
            # Check if tx_id is different and update if necessary
            if Tx.current_instance.tx_id != tx_id:
                print("Updating existing Tx instance")
                Tx.current_instance.update_config(tx_id)
            else:
                print("Existing Tx instance already has this tx_id")
                return  # Skip initialization if tx_id is the same
        else:
            # Set the current instance to this instance
            Tx.current_instance = self

    def call_tx_buffer(self, tx_buffer):
        self._tx_buffer = tx_buffer

    def transmit(self):
        if not self._tx_buffer.empty():
            data = self._tx_buffer.get()
            print(self.tx_id, "txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            self.hardware_interface.send_frame(self.tx_id, data)
            print(f"{Colors.blue}Transmitted : {Frame.hex(data)}{Colors.reset}")
            self.event_manager.publish('terminal', ['transmitted', data])

    def update_config(self, tx_id):
        # Update the current instance configuration
        self.tx_id = tx_id
        print(f"Tx instance updated with new tx_id: {tx_id}")


class Rx:
    current_instance = None  # Class-level reference to the current instance

    def __init__(self, hardware_interface, rx_id, event_manager):
        self.hardware_interface = hardware_interface
        self.rx_id = rx_id
        self.event_manager = event_manager

        if Rx.current_instance:
            # Check if rx_id is different and update if necessary
            if Rx.current_instance.rx_id != rx_id:
                print("Updating existing Rx instance")
                Rx.current_instance.update_config(rx_id)
            else:
                print("Existing Rx instance already has this rx_id")
                return  # Skip initialization if rx_id is the same
        else:
            # Set the current instance to this instance
            Rx.current_instance = self

    def call_rx_buffer(self, rx_buffer):
        self._rx_buffer = rx_buffer

    def receive(self):
        data, id = self.hardware_interface.receive_frame()

        # TODO: Comment the following 3 lines of code later, it was written to prevent the terminal from getting populated by zero value frames
        # Check if the frame is all zeros
        if all(byte == 0 for byte in data):
            return  # Ignore the frame and do not print or publish it

        if id == self.rx_id:
            print(data, "______", id)   # debug line
            self._rx_buffer.put(data) # this is not being used currently 
            print(f"{Colors.yellow}Received : {Frame.hex(data)}{Colors.reset}")
            self.event_manager.publish('data_received', data)
            self.event_manager.publish('terminal', ['received', data])

    def update_config(self, rx_id):
        # Update the current instance configuration
        self.rx_id = rx_id
        print(f"Rx instance updated with new rx_id: {rx_id}")


class CAN:
    def __init__(self, interface, tx_id, channel, baudrate, msg_type, event_manager: EventManager):
        self.event_manager = event_manager
        self.interface = interface
        self.hardware_interface = get_hardware_interface(interface, channel, baudrate, msg_type)
        self._tx_buffer = queue.Queue()
        self._rx_buffer = queue.Queue()
        self.event_manager.subscribe('rx_id', self.get_rx_id)
        self.tx = Tx(self.hardware_interface, tx_id, self.event_manager)
        self.tx.call_tx_buffer(self._tx_buffer)

    def update_interface(self, interface, tx_id, channel, baudrate, msg_type):
        self.interface = interface
        self.hardware_interface = get_hardware_interface(interface, channel, baudrate, msg_type)
        self.tx.update_config(tx_id)
        self.rx.update_config(self.rx_id)

    def transmit_data(self, data):
        self._tx_buffer.put(data)

    def get_rx_id(self, id):
        self.rx_id = id
        self.rx = Rx(self.hardware_interface, self.rx_id, self.event_manager)
        self.rx.call_rx_buffer(self._rx_buffer)

    def can_monitor(self):
        self.tx.transmit()
        self.rx.receive()

    """ def update_config_details(self, tx_id, rx_id, channel, baudrate, msg_type):
        print(tx_id, rx_id, channel, baudrate, msg_type)
        self.hardware_interface = get_hardware_interface("pcan", channel, baudrate, msg_type)
        print("hdfewiufhdjbfskdjfsddfekhtdsfbkashdwirukehfsamfetrueghslkfjkashfcdkjsvdksryeiwlefhdfha")
        self.tx = Tx(self.hardware_interface, tx_id, self._tx_buffer, self.event_manager)
        self.rx = Rx(self.hardware_interface, rx_id, self._rx_buffer, self.event_manager) """