from .UDSException import UDSException

class Frame:
    SINGLE_FRAME: int = 0
    FIRST_FRAME: int = 1
    CONSECUTIVE_FRAME: int = 2
    FLOW_CONTROL_FRAME: int = 3
    ERROR_FRAME: int = 4

    def validate_frame(self, response):
        """
        Validates the incoming frame and determines its type.
        """
        if (response[0] & 0xF0) == 0x00:
            return Frame.SINGLE_FRAME
        
        elif (response[0] & 0xF0) == 0x10:
            return Frame.FIRST_FRAME
            
        elif (response[0] & 0xF0) == 0x20:
            return Frame.CONSECUTIVE_FRAME
        
        elif (response[0] & 0xF0) == 0x30:
            return Frame.FLOW_CONTROL_FRAME
        
        # If the frame type is not recognized, raise an error
        raise Exception("Unexpected response format")

    def get_sid(self, frame):
        sid = frame[0]
        sid_int = int(sid, 16)
        if sid_int == 0x7F:
            pass
        else:
            sid_int = sid_int - 0x40
        return sid_int
        
    def extract_length(self, frame):
        # The length is extracted from the first two bytes for a first frame
        length = (((frame[0] & 0x0F) << 8) | frame[1]) - 6
        return length
    
    @staticmethod
    def negative_response(response):
        return True if response[1] == 0x7F else False
        
    @staticmethod
    def hex(msg):
        def process_hex(x):
            if isinstance(x, int):
                return f"0x{x:02X}"  # Format as two-digit hex
            elif isinstance(x, str):
                if x.startswith('0x'):
                    return x
                elif all(c in '0123456789abcdefABCDEF' for c in x):
                    return f"0x{int(x, 16):02X}"  # Convert and format as two-digit hex
                else:
                    try:
                        return f"0x{int(x, 0):02X}"
                    except ValueError:
                        print(f"Warning: Unable to convert to hex: {x}")
                        return x
            else:
                print(f"Warning: Unexpected type in hex conversion: {type(x)} for value: {x}")
                return str(x)

        return tuple(process_hex(m) for m in msg)
    
    def construct_flow_control(self, block_size, time_between_consecutive_frame):
        return (0x30, block_size, time_between_consecutive_frame, 0x00, 0x00, 0x00, 0x00, 0x00)
