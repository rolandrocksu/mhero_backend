import ipaddress

from django.core.exceptions import DisallowedHost
from django.conf import settings


class CustomAllowedHostsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        http_host = request.META.get("HTTP_HOST", "").split(':')[0]
        # If HTTP_HOST is empty, let CommonMiddleware handle it
        if not http_host:
            return self.get_response(request)

        allowed_private_range = ipaddress.ip_network('10.0.0.0/8')  # Define your private range

        try:
            # Check if host is a valid IP and within the allowed range
            ip = ipaddress.ip_address(http_host)
            if ip in allowed_private_range:
                # Bypass further host validation for private IPs
                # Set HTTP_HOST to a valid host to avoid DisallowedHost
                request.META['HTTP_HOST'] = settings.ALLOWED_HOSTS[0]
                return self.get_response(request)
        except ValueError:
            # Host is not an IP (e.g., it's a domain), pass to Django's default validation
            pass

        # Fall back to Django's ALLOWED_HOSTS for non-IP validation
        if http_host not in settings.ALLOWED_HOSTS:
            raise DisallowedHost(f"Host {http_host} not allowed")

        return self.get_response(request)
