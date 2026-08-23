from rest_framework import status

class TradeFlowException(Exception):
    """
    Base exception class for all TradeFlow applications.
    """
    default_message = "An unexpected application error occurred."
    default_code = "INTERNAL_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, code=None, status_code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        if status_code is not None:
            self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(TradeFlowException):
    default_message = "Invalid input or validation error."
    default_code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundException(TradeFlowException):
    default_message = "The requested resource was not found."
    default_code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class PermissionDeniedException(TradeFlowException):
    default_message = "You do not have permission to perform this action."
    default_code = "PERMISSION_DENIED"
    status_code = status.HTTP_403_FORBIDDEN


class ConflictException(TradeFlowException):
    default_message = "Resource state conflict."
    default_code = "CONFLICT"
    status_code = status.HTTP_409_CONFLICT
