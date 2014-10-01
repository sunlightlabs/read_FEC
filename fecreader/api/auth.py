from rest_framework import authentication
from rest_framework import exceptions

class DummyUser(object):
    def __init__(self, apikey):
        self.apikey = apikey

    def is_authenticated(self):
        return True

    def __unicode__(self):
        return self.apikey

class SpareribAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if not getattr(request, "apikey", None):
            raise exceptions.AuthenticationFailed('API key required.')

        return (DummyUser(request.apikey), None)