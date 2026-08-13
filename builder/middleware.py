from django.utils import timezone
from .models import Profile

class LastSeenMiddleware:
    """Middleware to update `Profile.last_seen` on each authenticated request."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            user = request.user
            if user.is_authenticated:
                Profile.objects.filter(user=user).update(last_seen=timezone.now())
        except Exception:
            # never break request on presence update
            pass
        return response
