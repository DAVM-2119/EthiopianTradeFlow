from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="Operation successful", status_code=status.HTTP_200_OK):
    """
    Standardized API success response payload structure:
    {
        "success": true,
        "data": {...},
        "message": "Operation successful"
    }
    """
    payload = {
        "success": True,
        "data": data if data is not None else {},
        "message": message,
    }
    return Response(payload, status=status_code)


def error_response(code="ERROR", message="An error occurred", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized API error response payload structure:
    {
        "success": false,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }
    """
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }
    return Response(payload, status=status_code)
