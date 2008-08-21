from django import template
from django.contrib.auth.models import AnonymousUser

from codereview import library

def nickname(email, arg=None):
    if isinstance(email, AnonymousUser):
        email = None
    return library.nickname(email, arg)

# Make filters global
template.defaultfilters.register.filter('nickname', nickname)