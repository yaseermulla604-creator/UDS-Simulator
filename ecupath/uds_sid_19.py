import queue
from . import Colors
from rich.table import Table
from rich.console import Console
from io import StringIO
from .frame import Frame

class Ox19:

    def __init__(self, uds_instance):
        self._buffer = queue.Queue()
        self.uds = uds_instance
        self.frame = Frame()
        self.subfunction_handlers = {
            0x01: self.handle_reportNumberOfDTCByStatusMask,
            0x02: self.handle_reportDTCByStatusMask,
            0x03: self.reportDTCSnapshotIdentification ,
            0x05: self.handle_reportDTCStoredDataByRecordNumber,
            0x0A: self.handle_reportSupportedDTC,
            0x12: self.reportNumberOfEmissionsOBDDTCByStatusMask,
            0x11: self.reportNumberOfMirrorMemoryDTCByStatusMask,
            0x13: self.handle_reportEmissionsOBDDTCByStatusMask,
            0x0F: self.reportMirrorMemoryDTCByStatusMask,
            0x0B: self.reportFirstTestFailedDTC,
            0x0C: self.reportFirstConfirmedDTC,
            0x0D: self.reportMostRecentTestFailedDTC,
            0x0E: self.reportMostRecentConfirmedDTC,
            0x14: self.reportDTCFaultDetectionCounter,
            0x15: self.reportDTCWithPermanentStatus
        }
        
    def buffer_frame(self, frame):
        self._buffer.put(frame)
        self.main()

    def main(self):
        if not self._buffer.empty():
            self.data = self._buffer.get()
            subfunction = int(self.data[1], 16)
            handler = self.subfunction_handlers.get(subfunction)
            if handler:
                handler(self.data[2:])
            else:
                print(f"Unsupported subfunction: {hex(subfunction)}")

    # subfunction 0x02
    def handle_reportDTCByStatusMask(self, data):
        self.data = data[1:]
        print(f"Handling reportDTCByStatusMask (0x02): {self.data}")
        print(f"{Colors.green}{self.data}{Colors.reset}")
        self.decoder(self.data)

    # subfunction 0x13
    def handle_reportEmissionsOBDDTCByStatusMask(self, data):
        print(f"Handling reportEmissionsOBDDTCByStatusMask (0x13): {data}")
        # Extract DTCStatusAvailabilityMask
        dtc_status_availability_mask = data[0]
        print(f"DTCStatusAvailabilityMask: {hex(dtc_status_availability_mask)}")

        # Process DTCs
        dtcs = data[1:]
        
        self.table = Table(title="Emissions-related OBD DTCs")
        self.table.add_column("DTC", style="cyan")
        self.table.add_column("Status", style="magenta")

        for i in range(0, len(dtcs), 4):
            if i + 3 < len(dtcs):
                dtc = (dtcs[i] << 16) | (dtcs[i+1] << 8) | dtcs[i+2]
                status = dtcs[i+3]
                
                dtc_str = f"{dtc:06X}"
                status_str = self.decode_dtc_status(status)
                
                self.table.add_row(dtc_str, status_str)

        # Capture the table output as a string
        with StringIO() as buffer:
            console = Console(file=buffer)
            console.print(self.table)
            table_string = buffer.getvalue()

        print(table_string)
        self.uds.added_from_sid(table_string)

    def decode_dtc_status(self, status):
        status_bits = {
            0: "testFailed",
            1: "testFailedThisOperationCycle",
            2: "pendingDTC",
            3: "confirmedDTC",
            4: "testNotCompletedSinceLastClear",
            5: "testFailedSinceLastClear",
            6: "testNotCompletedThisOperationCycle",
            7: "warningIndicatorRequested"
        }
        
        active_statuses = []
        for bit, description in status_bits.items():
            if status & (1 << bit):
                active_statuses.append(description)
        
        return " | ".join(active_statuses) if active_statuses else "No active status" 
       
    def decoder(self, received_data) -> None:
        print("decode_table")
        self.table = Table(title="Hex Values and Status Mask")
        self.table.add_column("Hex Values", justify="left")
        self.table.add_column("Status/Counter/Snapshot Record Number", justify="left")
        self.console = Console()

        # Ensure that data contains integers
        hex_data = self.frame.hex(received_data)

        # Convert hex strings to integers if necessary
        data = []
        for item in hex_data:
            if isinstance(item, str):
                if item.startswith('0x'):
                    item = int(item, 16)  # Convert hex string with '0x' to integer
                else:
                    item = int(item, 16)  # Convert plain hex string to integer
            data.append(item)  # Append each converted item

        print(f"Data length: {len(data)}")  # Debug print for data length

        for i in range(0, len(data), 4):
            if i + 3 < len(data):  # Ensure there are enough bytes for a complete set
                combined_hex_value = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
                status_mask = data[i + 3]
                
                hex_value_str = f"{combined_hex_value:06X}"
                status_mask_str = f"{status_mask:02X}"
                print("Tableee")  # Debug print to verify decode_table call
                self.decode_table(hex_value_str, status_mask_str)
        
        # Capture the table output as a string
        with StringIO() as buffer:
            self.console = Console(file=buffer)
            self.console.print(self.table)
            table_string = buffer.getvalue()

        print(table_string)  # Print the captured table string

        try:
            # Print to console and add to uds
            self.uds.added_from_sid(table_string)
            print("Added table to uds bufferrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        except Exception as e:
            print(f"Error printing table: {e}")

    def hex_to_bin(self, hex_value):
        print("hex_to_bin")
        if isinstance(hex_value, str):
            hex_value = int(hex_value, 16)
        binary_string = bin(hex_value)[2:].zfill(8)
        return binary_string    

    def decode_table(self, hex_value_str, status_mask_str) -> None:
        print("decode_table")
        system_specific_dtc = int(hex_value_str, 16) & 0xF00000
        system_specific_value = self.hex_to_bin(system_specific_dtc)[:2]
        
        my_dict = {
            '00': 'Power Train',
            '01': 'Chassis',
            '10': 'Body',
            '11': 'Network'
        }
        
        system_type = my_dict.get(system_specific_value, "Unknown")
        
        status_mask_dict = {
            '00': 'Test Failed',
            '01': 'Test Failed This Operation Cycle',
            '02': 'Pending DTC',
            '03': 'Confirmed DTC',
            '04': 'Test Not COmpleted Since Last Clear',
            '05': 'Test Failed Since Last Clear',
            '06': 'Test Not Completed This Operation Cycle',
            '07': 'Warning Indicator Request',
            
        }
        def get_status_message(status_mask):
            message = []
            for bit_position in range(8):
                if status_mask & (1 << bit_position):
                    key = f"{bit_position:02X}"  # Correct formatting here
                    if key in status_mask_dict:
                        message.append(status_mask_dict[key])
            return ' & '.join(message)
            
        status_mask = int(status_mask_str, 16)
        status = get_status_message(status_mask)
        
        self.table.add_row(f"{hex_value_str} ({system_type})", f"{status_mask_str} ({status})")

    # subfunction 0x01
    def handle_reportNumberOfDTCByStatusMask(self, data):
        print(f"Handling reportNumberOfDTCByStatusMask (0x01): {data}")
        print("0x01 Count: ", data[2])
        self.uds.added_from_sid(data[2])

    # subfunction 0x0A
    def handle_reportSupportedDTC(self, data):
        print(f"Handling reportSupportedDTC (0x0A): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.one_column_table(data)

    def one_column_table(self, data):
        self.dtc_data = data
        self.console = Console()
        self.table = Table(title="Report Suported DTCs")

        # Add a single column
        self.table.add_column("DTCs", style="cyan")

        # Process the tuple in groups of 3
        for i in range(0, len(self.dtc_data), 3):
            group = self.dtc_data[i:i+3]
            # Join the group values with spaces
            row_content = " ".join(group)
            self.table.add_row(row_content)

        #self.console.print(self.table)
        # Capture the table output as a string
        with StringIO() as s_table:
            self.console = Console(file=s_table)
            self.console.print(self.table)
            string_table = s_table.getvalue()

        print(string_table)  # Print the captured table string
        self.uds.added_from_sid(string_table)

    # subfunction 0x12
    def reportNumberOfEmissionsOBDDTCByStatusMask(self, data):
        print(f"Handling reportNumberOfDTCByStatusMask (0x12): {data}")
        print("0x12 Count: ", data[2])
        self.uds.added_from_sid(data[2])

    # subfunction 0x11
    def reportNumberOfMirrorMemoryDTCByStatusMask(self, data):
        print(f"Handling reportNumberOfDTCByStatusMask (0x11): {data}")
        print("0x11 Count: ", data[2])
        self.uds.added_from_sid(data[2])

    # subfunction 0x0F
    def reportMirrorMemoryDTCByStatusMask(self, data):
        self.data = data[1:]
        print(f"Handling reportNumberOfDTCByStatusMask (0x0F): {self.data}")
        print(f"{Colors.green}{self.data}{Colors.reset}")
        self.decoder(self.data)

    # subfunction 0x0B
    def reportFirstTestFailedDTC(self, data):
        print(f"reportFirstTestFailedDTC (0x0B): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.decoder(data)

    # subfunction 0x0C
    def reportFirstConfirmedDTC (self, data):
        print(f"reportFirstConfirmedDTC (0x0C): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.decoder(data)

    # subfunction 0x0D
    def reportMostRecentTestFailedDTC(self, data):
        print(f"reportMostRecentTestFailedDTC (0x0D): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.decoder(data)

    # subfunction 0x0E
    def reportMostRecentConfirmedDTC(self, data):
        print(f"reportMostRecentConfirmedDTC (0x0E): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.decoder(data)

    # subfunction 0x14
    def reportDTCFaultDetectionCounter(self, data):
        print(f"reportDTCFaultDetectionCounter (0x14): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.decoder(data)

    # subfunction 0x15
    def reportDTCWithPermanentStatus(self, data):
        print(f"reportDTCWithPermanentStatus (0x15): {data}")
        print(f"{Colors.green}{data}{Colors.reset}")
        self.decoder(data)

    # subfunction 0x05
    def handle_reportDTCStoredDataByRecordNumber(self, data):
        print(f"Handling reportDTCStoredDataByRecordNumber (0x05): {data}")
        
        record_number = data[0]
        print(f"DTCStoredDataRecordNumber: {hex(record_number)}")

        self.table = Table(title="DTC Stored Data")
        self.table.add_column("Parameter", style="cyan")
        self.table.add_column("Value", style="magenta")

        index = 1
        while index < len(data):
            if index + 3 < len(data):
                dtc = (data[index] << 16) | (data[index+1] << 8) | data[index+2]
                status = data[index+3]
                
                dtc_str = f"{dtc:06X}"
                status_str = self.decode_dtc_status(status)
                
                self.table.add_row("DTC", dtc_str)
                self.table.add_row("Status", status_str)
                
                index += 4

                if index < len(data):
                    num_identifiers = data[index]
                    self.table.add_row("Number of Identifiers", str(num_identifiers))
                    index += 1

                    for _ in range(num_identifiers):
                        if index + 1 < len(data):
                            identifier = (data[index] << 8) | data[index+1]
                            index += 2
                            
                            stored_data = []
                            while index < len(data) and data[index] != 0x00:  # Assume 0x00 as separator
                                stored_data.append(f"{data[index]:02X}")
                                index += 1
                            
                            self.table.add_row(f"Data Identifier {identifier:04X}", " ".join(stored_data))
                            index += 1  # Skip the separator

        # Capture the table output as a string
        with StringIO() as buffer:
            console = Console(file=buffer)
            console.print(self.table)
            table_string = buffer.getvalue()

        print(table_string)
        self.uds.added_from_sid(table_string)    
    
    # subfunction 0x03
    def reportDTCSnapshotIdentification(self,data):
        self.data = data[1:]
        print(f"Handling reportDTCSnapshotIdentification (0x03): {self.data}")
        print(f"{Colors.green}{self.data}{Colors.reset}")
        self.decoder(self.data)