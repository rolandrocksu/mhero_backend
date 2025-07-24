from drf_yasg import openapi
from rest_framework import serializers


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class TokenVerifyResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField()


class LogoutResponseSerializer(serializers.Serializer):
    pass


class TokenObtainPairResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user_id = serializers.IntegerField()
    email = serializers.CharField(allow_null=True)


DEFAULT_STATUS_CODES = {
    "400": openapi.Response(
        description="Invalid body params",
    ),
    "401": openapi.Response(
        description="Invalid authorization token in the request headers",
    ),
}


TOKEN_REFRESH_SCHEMA = dict(
    operation_description="Refresh access token.",
    responses={
        "200": openapi.Response(
            description="Successful refresh",
            schema=TokenRefreshResponseSerializer,
        ),
        "401": "Unauthorized: Invalid refresh token",
    },
)

TOKEN_VERIFY_SCHEMA = dict(
    operation_description="Verify access token.",
    responses={
        "200": openapi.Response(
            description="Verified",
        ),
        "401": openapi.Response(
            description="Not valid",
            schema=TokenVerifyResponseSerializer,
        ),
    },
)

LOGOUT_SCHEMA = dict(
    operation_description="Logout current user.",
    responses={
        "205": openapi.Response(
            description="Successful logout",
            schema=LogoutResponseSerializer,
        ),
        **DEFAULT_STATUS_CODES,
    },
)


SOCIAL_LOGIN_SCHEMA = dict(
    responses={
        '200': openapi.Response(
            description="Successful login",
            schema=TokenObtainPairResponseSerializer,
        ),
        '201': openapi.Response(
            description="Successful registration",
            schema=TokenObtainPairResponseSerializer,
        ),
    }
)
