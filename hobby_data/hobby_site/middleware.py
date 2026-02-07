from django.utils import timezone
from tzlocal import get_localzone


class LocalTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.local_tz = get_localzone()

    def __call__(self, request):
        timezone.activate(self.local_tz)
        try:
            return self.get_response(request)
        finally:
            timezone.deactivate()
