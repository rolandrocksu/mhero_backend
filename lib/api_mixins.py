from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class PublicAPIMixin:
    authentication_classes = []
    permission_classes = []


class AuthenticatedAPIMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
