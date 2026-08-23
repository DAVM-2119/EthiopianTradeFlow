import uuid
from apps.core.responses import success_response, error_response
from apps.core.utils import is_valid_uuid, get_utc_now

def test_response_helpers():
    succ = success_response(data={"item": 1}, message="Created", status_code=201)
    assert succ.status_code == 201
    assert succ.data == {
        "success": True,
        "data": {"item": 1},
        "message": "Created",
    }

    err = error_response(code="TEST_ERR", message="Failed", details={"row": 5}, status_code=400)
    assert err.status_code == 400
    assert err.data == {
        "success": False,
        "error": {
            "code": "TEST_ERR",
            "message": "Failed",
            "details": {"row": 5},
        }
    }


def test_uuid_and_utc_helpers():
    u = uuid.uuid4()
    assert is_valid_uuid(u) is True
    assert is_valid_uuid(str(u)) is True
    assert is_valid_uuid("invalid-uuid-string") is False
    assert is_valid_uuid(12345) is False

    now = get_utc_now()
    assert now.tzinfo is not None
