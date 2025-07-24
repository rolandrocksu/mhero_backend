from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import UntypedToken


def is_valid_token(token: str) -> bool:
    """Check whether the given token is valid and not expired."""
    try:
        UntypedToken(token)
        return True
    except TokenError:
        return False
