# Project Overview 
The UDS/CAN GUI application is a powerful tool for automotive diagnostics, designed to streamline the process of interacting with vehicle ECUs. With a robust Python-based implementation, comprehensive domain knowledge in UDS and CAN protocols, and a user-friendly GUI, this application is well-suited for both developers and automotive engineers. Understanding its components and how they work together is key to effectively using and modifying the application.

# Technical Requirements
### Python:

- Version 3.12.4 or later
- Proficiency in Python programming, including:
    - Object-Oriented Programming concepts
    - Asynchronous programming

Here's a more structured version of the instructions:

### How to Run the Project

To get the project up and running, follow these steps:

1. **Install Dependencies** (First-time Setup):
   - **Backend**: Install the `pywebview` library by running the following command:
     ```bash
     pip install pywebview
     ```
   - **Frontend**: Navigate to the `vanalyzer` folder and install the necessary dependencies by running:
     ```bash
     npm i
     ```

2. **Build and Launch the Project**:
   - Return to the root of the project directory.
   - Execute the `r.bat` script to build the frontend and launch the project:
     ```bash
     r.bat
     ```
   - The script will automatically build the frontend and start the project by running the `vanalyzer.py` file.


### Development Environment:

- A suitable Integrated Development Environment (IDE) or text editor
- Git for version control (recommended)

### Domain Knowledge
- UDS (Unified Diagnostic Services) Protocol:

    - Understanding of UDS concepts and operations
    - Familiarity with UDS services, particularly:
        - 0x19: Read DTC Information
        - 0x22: Read Data By Identifier
        - 0x2E: Write Data By Identifier
    - Knowledge of UDS message structure and flow

### CAN (Controller Area Network) Protocol:

- Fundamentals of CAN communication
- Understanding of CAN message format and IDs
- Familiarity with CAN bus speed and timing

### Automotive Diagnostics:

- Basic understanding of automotive electronic systems
- Familiarity with ECUs (Electronic Control Units)
- Knowledge of DTCs (Diagnostic Trouble Codes)

### Additional Skills

- Understanding of event-driven programming
- Networking:
    - Basic understanding of network protocols
    - Familiarity with serial communication

### Debugging and Testing:

- Proficiency in debugging Python applications
- Experience with testing GUI applications

### Hardware
- Access to a CAN interface device compatible with the application
- A vehicle or ECU simulator for testing UDS communications

### Downloads
- Link : https://www.peak-system.com/PCAN-USB.199.0.html?L=1
<br>(Download Device Driver Setup for Windows)

### Additional
- Use methods from PCAN Basic API for sending and receiving messages over PCAN Hardware

<br>

# CAN and UDS Implementation Documentation

## CAN Class

### Purpose
Provides a high-level interface for CAN communication.

### Key Components
- Tx (transmission)
- Rx (reception)

### Main Methods
- `__init__()`: Initializes the CAN interface by setting up the required hardware, subscribing to `get_rx_id`, and setting all parameters for the TX class.
- `transmit_data()`: Queues data for transmission.
- `get_rx_id()`: Sets the Rx class.
- `can_monitor()`: Continuously monitors transmissions and receptions.

## CAN_TP Class

### Purpose
Implements the CAN Transport Protocol.

### Key Components
- CAN interface
- Frame handling

### Main Methods
- `__init__()`: Initializes CAN_TP and subscribes to the `get_data` function for publishing. Uses threading for data transmission.
- `send_data()`: Calls the `transmit_data` function from the CAN class to transmit data.
- `process_frame()`: Processes incoming frames, checking if they are zero, single, first, consecutive, or flow control frames using the Frame class. Routes single and consecutive frames to UDS.
- `send_multi_frame()`: Handles multi-frame transmissions, particularly for SID 0x2E where the user writes data and the ECU returns flow control.
- `send_consecutive_frame()`: Used for sending large data volumes by filling the `frame_tuple` and `buffer_to_can` queue.
- `cantp_monitor()`: Monitors the `buffer_from_uds` and `buffer_to_can` queues.

## EventManager Class

### Purpose
Implements the publish-subscribe pattern.

### Key Methods
- `__init__()`: Creates a dictionary named `subscribers` to store event types and their corresponding functions.
- `subscribe()`: Sets the key and its value in the `subscribers` dictionary.
- `publish()`: Checks if the event type is present in the dictionary and calls the corresponding function with the provided data.

## Frame Class

### Purpose
Provides utilities for CAN frame handling.

### Key Methods
- `validate_frame()`: Checks the first byte of the frame to determine if it's a single, first, or control frame.
- `extract_length()`: Extracts the length of the data from the first two bytes of the frame.
- `check_neg_response()`: Maps the first byte of the frame to the corresponding UDSException.
- `construct_flow_control()`: Sends flow control frames.

## HardwareInterface Class

### Purpose
Serves as an abstract base class for CAN hardware interfaces.

### Implementations
- PCAN
- Vector hardware

### Key Methods
- `send_frame()`: Sets all parameters required to send frames using the PCAN class.
- `receive_frame()`: Reads incoming data.
- `get_hardware_interface()`: (Not detailed in the original text)

## UDS Class

### Purpose
Forms the core of the UDS implementation.

### Key Features
- Manages diagnostic sessions
- Implements request queue
- Handles timing (P2 and P2* timers)

### Important Methods
- `__init__()`: Sets parameters for the CAN_TP class, publishes `get_rx_id`, subscribes to `process_response`, and creates a handler dictionary for user requests.
- `start_session()`: Checks if a session has started or sends START_SESSION.
- `send_request()`: Called by the GUI to send data into the `buffer_to_can` queue.
- `process_immediate_request()`: Checks if the `immediate_request` is empty and sends data into the `buffer_from_uds` queue.
- `process_request()`: Called via the publish method when data is received from CAN_TP.
- `handle_response()`: Handles the response, updating timers or reading UDSExceptions as needed.

## 0x19 Class (ReadDTCInformation Service)

### Purpose
Handles UDS Service ID 0x19 for reading DTCs.

### Key Features
- Supports multiple subfunctions
- Decodes DTC information

### Important Methods
- `__init__()`: Creates a buffer to store data and a dictionary to map subfunctions.
- `main()`: Checks if the buffer is empty and maps to the required subfunction based on the key value.
- `handle_reportDTCByStatusMask()`
- `handle_reportDTCExtDataRecordByDTCNumber()`
- `decode_dtc_status()`

---

For detailed information on subfunction logic, please refer to the ISO 14229-1:2013 documentation.

## 0x22 Class (ReadDataByIdentifier Service)

### Purpose
Handles UDS Service ID 0x22.

### Key Methods
- `buffer_frame()`: Puts data in the buffer and calls the main function.
- `main()`: Calls `uds.added_from_sid` to print data in tabular form.

## 0x2E Class (WriteDataByIdentifier Service)

### Purpose
Handles UDS Service ID 0x2E.

### Key Methods
- `buffer_frame()` : Puts data in the buffer and calls the main function.

-  `main()`: Calls uds.added_from_sid to print data in tabular form.

## UDSException Class

### Purpose
Handles UDS-specific exceptions.

### Key Features
- Defines exceptions based on Negative Response Codes (NRCs)
- Provides human-readable error messages

### Important Methods
- `create_exception()`
- `get_error_message()`



# Further Code Improvements


- Extending Service IDs: To incorporate additional Service IDs (SIDs), create a dedicated file named after the SID and implement a corresponding class within it. Then, register this new SID class in the handler dictionary of the UDS class.

- Integrating LIN Protocol: If LIN (Local Interconnect Network) communication is required instead of CAN, develop a LIN-specific class. This class can be integrated with the main application by utilizing the publish-subscribe pattern, ensuring seamless communication with the existing framework.

- Adding Subfunctions (in SID 0x19): To introduce new subfunctions under SID 0x19, define a function with the subfunction name and add it to the  subfunction_handlers dictionary within the uds_sid_19 file. 
<br>If modifications are to be made for transmitting and receiving of data with respect to any sub function then it should be made within the `CAN_TP` class. These changes will allow for the proper handling and transmission of the new subfunctions, ensuring they are processed correctly within the application.
