from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_205_RESET_CONTENT,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.api.schemas import (
    LOGOUT_SCHEMA,
    TOKEN_REFRESH_SCHEMA,
    TOKEN_VERIFY_SCHEMA,
    SOCIAL_LOGIN_SCHEMA,
)
from accounts.api.serializers import (
    LogoutSerializer,
    GoogleAuthSerializer,
    AppleAuthSerializer,
)
from accounts.models import MheroUser
from lib.api_mixins import PublicAPIMixin

User = get_user_model()


@method_decorator(name="post", decorator=swagger_auto_schema(**TOKEN_REFRESH_SCHEMA))
class TokenRefreshAPIView(TokenRefreshView):
    pass


@method_decorator(name="post", decorator=swagger_auto_schema(**TOKEN_VERIFY_SCHEMA))
class TokenVerifyAPIView(TokenVerifyView):
    pass


@method_decorator(name="post", decorator=swagger_auto_schema(**LOGOUT_SCHEMA))
class LogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_205_RESET_CONTENT)


@method_decorator(
    name='post',
    decorator=swagger_auto_schema(**SOCIAL_LOGIN_SCHEMA)
)
class BaseSocialLoginAPIView(PublicAPIMixin, GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = serializer.get_or_create()

        # Activate user every time he/she signs in if he/she is inactive
        if not user.is_active:
            user.is_active = True
            user.save()

        token = RefreshToken.for_user(user)
        update_last_login(None, user)

        data = {
            'access': str(token.access_token),
            'refresh': str(token),
            "user_id": user.id,
            "email": user.email,
            'tokens_used_today': user.tokens_used_today,
            'remaining_tokens_today': user.remaining_tokens_today
        }
        status = HTTP_201_CREATED if created else HTTP_200_OK
        return Response(data, status=status)


class GoogleLoginAPIView(BaseSocialLoginAPIView):
    serializer_class = GoogleAuthSerializer


class AppleLoginAPIView(BaseSocialLoginAPIView):
    serializer_class = AppleAuthSerializer


class TestLoginView(APIView):
    # WARNING: Only enable this in development!
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email required"}, status=HTTP_400_BAD_REQUEST)
        if email != "test@test.com":
            return Response({"detail": "User not found"}, status=HTTP_404_NOT_FOUND)

        user, created = MheroUser.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()  # No password, for safety
            user.save()

        token = RefreshToken.for_user(user)
        data = {
            'access': str(token.access_token),
            'refresh': str(token),
            "user_id": user.id,
            "email": user.email,
            'tokens_used_today': user.tokens_used_today,
            'remaining_tokens_today': user.remaining_tokens_today
        }
        return Response(data)
