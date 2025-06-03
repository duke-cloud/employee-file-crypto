# cryptoapp/decorators.py
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def role_required(*roles):
    def check(u):
        if not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        if u.groups.filter(name__in=roles).exists():
            return True
        raise PermissionDenied
    return user_passes_test(check, login_url='login', redirect_field_name=None)
