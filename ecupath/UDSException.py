class UDSException(Exception):
    """Exception for UDS errors"""
    def __init__(self, nrc):
        self.nrc = nrc
        self.message = self.__class__.get_error_message(nrc)
        super().__init__(self.message)

    @classmethod
    def get_error_message(cls, nrc):
        error_messages = {
            '0x10': "General reject",
            '0x11': "Service not supported",
            '0x12': "Sub-function not supported",
            '0x13': "Incorrect message length or invalid format",
            '0x14': "Response too long",
            '0x21': "Busy repeat request",
            '0x22': "Conditions not correct",
            '0x24': "Request sequence error",
            '0x25': "No response from subnet component",
            '0x26': "Failure prevents execution of requested action",
            '0x31': "Request out of range",
            '0x33': "Security access denied",
            '0x35': "Invalid key",
            '0x36': "Exceed number of attempts",
            '0x37': "Required time delay not expired",
            '0x38': "Secure data transmission not supported",
            '0x39': "Secure data transmission not allowed",
            '0x3A': "Secure data transmission error",
            '0x3B': "Secure data transmission busy",
            '0x3F': "General programming failure",
            '0x41': "Wrong block sequence counter",
            '0x42': "Response pending",
            '0x43': "Sub-function not supported in active session",
            '0x45': "General programming failure",
            '0x71': "Transfer aborted",
            '0x72': "Incorrect block sequence counter",
            '0x73': "Unsupported transfer type",
            '0x78': "Request correctly received, response pending",
            '0x7E': "Sub-function not supported in active session",
            '0x7F': "Service not supported in active session"
        }
        return error_messages.get(nrc, f"Unknown NRC: {nrc}")

    @staticmethod
    def create_exception(nrc):
        exception_classes = {
            0x10: GeneralRejectException,
            0x11: ServiceNotSupportedException,
            0x12: SubFunctionNotSupportedException,
            0x13: IncorrectMessageLengthOrInvalidFormatException,
            0x14: ResponseTooLongException,
            0x21: BusyRepeatRequestException,
            0x22: ConditionsNotCorrectException,
            0x24: RequestSequenceErrorException,
            0x25: NoResponseFromSubnetComponentException,
            0x26: FailurePreventsExecutionOfRequestedActionException,
            0x31: RequestOutOfRangeException,
            0x33: SecurityAccessDeniedException,
            0x35: InvalidKeyException,
            0x36: ExceedNumberOfAttemptsException,
            0x37: RequiredTimeDelayNotExpiredException,
            0x38: SecureDataTransmissionNotSupportedException,
            0x39: SecureDataTransmissionNotAllowedException,
            0x3A: SecureDataTransmissionErrorException,
            0x3B: SecureDataTransmissionBusyException,
            0x3F: GeneralProgrammingFailureException,
            0x41: WrongBlockSequenceCounterException,
            0x42: ResponsePendingException,
            0x43: SubFunctionNotSupportedInActiveSessionException,
            0x45: GeneralProgrammingFailureException,
            0x71: TransferAbortedException,
            0x72: IncorrectBlockSequenceCounterException,
            0x73: UnsupportedTransferTypeException,
            0x78: RequestCorrectlyReceivedResponsePendingException,
            0x7E: SubFunctionNotSupportedInActiveSessionException,
            0x7F: ServiceNotSupportedInActiveSessionException
        }
        exception_class = exception_classes.get(nrc, UDSException)
        return exception_class(nrc)

class GeneralRejectException(UDSException):
    def __init__(self, nrc=0x10):
        super().__init__(nrc)

class ServiceNotSupportedException(UDSException):
    def __init__(self, nrc=0x11):
        super().__init__(nrc)

class SubFunctionNotSupportedException(UDSException):
    def __init__(self, nrc=0x12):
        super().__init__(nrc)

class IncorrectMessageLengthOrInvalidFormatException(UDSException):
    def __init__(self, nrc=0x13):
        super().__init__(nrc)

class ResponseTooLongException(UDSException):
    def __init__(self, nrc=0x14):
        super().__init__(nrc)

class BusyRepeatRequestException(UDSException):
    def __init__(self, nrc=0x21):
        super().__init__(nrc)

class ConditionsNotCorrectException(UDSException):
    def __init__(self, nrc=0x22):
        super().__init__(nrc)

class RequestSequenceErrorException(UDSException):
    def __init__(self, nrc=0x24):
        super().__init__(nrc)

class NoResponseFromSubnetComponentException(UDSException):
    def __init__(self, nrc=0x25):
        super().__init__(nrc)

class FailurePreventsExecutionOfRequestedActionException(UDSException):
    def __init__(self, nrc=0x26):
        super().__init__(nrc)

class RequestOutOfRangeException(UDSException):
    def __init__(self, nrc=0x31):
        super().__init__(nrc)

class SecurityAccessDeniedException(UDSException):
    def __init__(self, nrc=0x33):
        super().__init__(nrc)

class InvalidKeyException(UDSException):
    def __init__(self, nrc=0x35):
        super().__init__(nrc)

class ExceedNumberOfAttemptsException(UDSException):
    def __init__(self, nrc=0x36):
        super().__init__(nrc)

class RequiredTimeDelayNotExpiredException(UDSException):
    def __init__(self, nrc=0x37):
        super().__init__(nrc)

class SecureDataTransmissionNotSupportedException(UDSException):
    def __init__(self, nrc=0x38):
        super().__init__(nrc)

class SecureDataTransmissionNotAllowedException(UDSException):
    def __init__(self, nrc=0x39):
        super().__init__(nrc)

class SecureDataTransmissionErrorException(UDSException):
    def __init__(self, nrc=0x3A):
        super().__init__(nrc)

class SecureDataTransmissionBusyException(UDSException):
    def __init__(self, nrc=0x3B):
        super().__init__(nrc)

class GeneralProgrammingFailureException(UDSException):
    def __init__(self, nrc=0x3F):
        super().__init__(nrc)

class WrongBlockSequenceCounterException(UDSException):
    def __init__(self, nrc=0x41):
        super().__init__(nrc)

class ResponsePendingException(UDSException):
    def __init__(self, nrc=0x42):
        super().__init__(nrc)

class SubFunctionNotSupportedInActiveSessionException(UDSException):
    def __init__(self, nrc=0x43):
        super().__init__(nrc)

class TransferAbortedException(UDSException):
    def __init__(self, nrc=0x71):
        super().__init__(nrc)

class IncorrectBlockSequenceCounterException(UDSException):
    def __init__(self, nrc=0x72):
        super().__init__(nrc)

class UnsupportedTransferTypeException(UDSException):
    def __init__(self, nrc=0x73):
        super().__init__(nrc)

class RequestCorrectlyReceivedResponsePendingException(UDSException):
    def __init__(self, nrc=0x78):
        super().__init__(nrc)

class SubFunctionNotSupportedInActiveSessionException(UDSException):
    def __init__(self, nrc=0x7E):
        super().__init__(nrc)

class ServiceNotSupportedInActiveSessionException(UDSException):
    def __init__(self, nrc=0x7F):
        super().__init__(nrc)