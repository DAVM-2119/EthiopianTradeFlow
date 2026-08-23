from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from .base import TradeFlowException

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler providing consistent error JSON format across all APIs:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {}
        }
    }
    """
    # First, handle TradeFlow custom exceptions directly
    if isinstance(exc, TradeFlowException):
        error_payload = {
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        }
        return Response(error_payload, status=exc.status_code)

    # Standard DRF exception handling for builtin DRF exceptions
    response = exception_handler(exc, context)

    if response is not None:
        error_code = "API_ERROR"
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = "VALIDATION_ERROR"
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "UNAUTHENTICATED"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_code = "PERMISSION_DENIED"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "NOT_FOUND"
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            error_code = "METHOD_NOT_ALLOWED"

        details = response.data if isinstance(response.data, (dict, list)) else {}
        message = "An error occurred while processing your request."

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = str(response.data["detail"])
            elif len(response.data) == 1 and isinstance(next(iter(response.data.values())), list):
                field, errs = next(iter(response.data.items()))
                message = f"{field}: {errs[0]}" if errs else message

        response.data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details,
            }
        }

    return response
