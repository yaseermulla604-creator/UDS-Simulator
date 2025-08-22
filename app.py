from ecupath import UDS
from ecupath import EventManager
import time

class App:
    TESTER_PRESENT = (0x3E, 0x00)
    STOP_MONITORING = False

    def __init__(self, interface, tx_id, rx_id, channel, baud_rate, message_type, event_manager: EventManager):
        self.interface = interface
        self.tx_id = tx_id
        self.rx_id = rx_id
        self.channel = channel
        self.baud_rate = baud_rate
        self.message_type = message_type
        self.event_manager = event_manager
        self.uds = UDS(interface, tx_id, rx_id, channel, baud_rate, message_type, event_manager)
        self.monitoring = False
        self.sending_tester_present = False

    def update_interface(self, interface, tx_id, rx_id, channel, baud_rate, message_type):
        self.stop_interface()  # Stop the current interface before updating
        self.interface = interface
        self.tx_id = tx_id
        self.rx_id = rx_id
        self.channel = channel
        self.baud_rate = baud_rate
        self.message_type = message_type
        self.uds.update_interface(interface, tx_id, rx_id, channel, baud_rate, message_type)

    def start_monitoring(self):
        self.monitoring = True
        self.STOP_MONITORING = False
        self.uds.start_session()
        time.sleep(0.01)
        while self.monitoring and not self.STOP_MONITORING:
            self.monitor()
            self.send_tester_present()
            time.sleep(0.01)

    def stop_monitoring(self):
        self.STOP_MONITORING = True
        self.monitoring = False

    def monitor(self):
        if not self.sending_tester_present:
            self.uds.process_request_queue()
            self.uds.can_tp.cantp_monitor()
            self.uds.can_tp.can.can_monitor()

    def send_tester_present(self):
        self.sending_tester_present = True
        self.uds.send_request(App.TESTER_PRESENT, immediate=True)
        self.sending_tester_present = False
        time.sleep(4)

    def get_uds(self):
        return self.uds