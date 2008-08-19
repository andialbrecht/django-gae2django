from django.conf import settings
from django.contrib.auth.models import User


def get_current_user():
    from gae_django import middleware
    return middleware.get_current_user()

def is_current_user_admin():
    user = get_current_user()
    if user:
        return user.is_superuser
    return False

def create_login_url(redirect):
    return settings.LOGIN_URL+'?next='+redirect

def create_logout_url(redirect):
    return settings.LOGOUT_URL+'?next='+redirect