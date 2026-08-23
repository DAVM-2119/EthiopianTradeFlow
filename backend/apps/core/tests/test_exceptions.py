import pytest
from rest_framework import status
from apps.core.exceptions import (
    TradeFlowException,
    ValidationException,
    NotFoundException,
    PermissionDeniedException,
    ConflictException,
    custom_exception_handler,
)

def test_tradeflow_exceptions():
    base_exc = TradeFlowException("Base error", code="BASE_ERR", status_code=500)
    assert base_exc.message == "Base error"
    assert base_exc.code == "BASE_ERR"
    assert base_exc.status_code == 500

    val_exc = ValidationException(message="Invalid field", details={"field": "required"})
    assert val_exc.status_code == status.HTTP_400_BAD_REQUEST
    assert val_exc.code == "VALIDATION_ERROR"
    assert val_exc.details == {"field": "required"}

    nf_exc = NotFoundException()
    assert nf_exc.status_code == status.HTTP_404_NOT_FOUND
    assert nf_exc.code == "NOT_FOUND"

    perm_exc = PermissionDeniedException()
    assert perm_exc.status_code == status.HTTP_403_FORBIDDEN

    conf_exc = ConflictException()
    assert conf_exc.status_code == status.HTTP_409_CONFLICT


def test_custom_exception_handler():
    exc = ValidationException(message="Invalid data", details={"foo": "bar"})
    resp = custom_exception_handler(exc, {})
    assert resp.status_code == 400
    assert resp.data == {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid data",
            "details": {"foo": "bar"}
        }
    }
