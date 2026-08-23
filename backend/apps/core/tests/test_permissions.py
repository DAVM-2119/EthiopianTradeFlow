from unittest.mock import MagicMock
from apps.core.permissions import IsStaffUser, ReadOnly, IsOwnerOrReadOnly

def test_is_staff_user_permission():
    perm = IsStaffUser()
    request_anon = MagicMock(user=None)
    assert perm.has_permission(request_anon, None) is False

    request_non_staff = MagicMock(user=MagicMock(is_authenticated=True, is_staff=False))
    assert perm.has_permission(request_non_staff, None) is False

    request_staff = MagicMock(user=MagicMock(is_authenticated=True, is_staff=True))
    assert perm.has_permission(request_staff, None) is True


def test_read_only_permission():
    perm = ReadOnly()
    req_get = MagicMock(method='GET')
    req_post = MagicMock(method='POST')
    assert perm.has_permission(req_get, None) is True
    assert perm.has_permission(req_post, None) is False


def test_is_owner_or_read_only():
    perm = IsOwnerOrReadOnly()
    user1 = MagicMock(id='u-1')
    user2 = MagicMock(id='u-2')

    obj = MagicMock(owner=user1)
    req_get = MagicMock(method='GET', user=user2)
    req_post_owner = MagicMock(method='POST', user=user1)
    req_post_other = MagicMock(method='POST', user=user2)

    assert perm.has_object_permission(req_get, None, obj) is True
    assert perm.has_object_permission(req_post_owner, None, obj) is True
    assert perm.has_object_permission(req_post_other, None, obj) is False
