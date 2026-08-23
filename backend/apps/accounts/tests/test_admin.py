from django.contrib import admin
from apps.accounts.models import User
from apps.accounts.admin import UserAdmin

def test_user_admin_registration():
    assert admin.site.is_registered(User)
    admin_obj = admin.site._registry[User]
    assert isinstance(admin_obj, UserAdmin)
    assert 'email' in admin_obj.list_display
    assert 'role' in admin_obj.list_display
    assert 'status' in admin_obj.list_display
    assert 'is_verified' in admin_obj.list_display
    assert 'role' in admin_obj.list_filter
    assert 'status' in admin_obj.list_filter
    assert 'email' in admin_obj.search_fields
