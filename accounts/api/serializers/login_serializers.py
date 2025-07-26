from abc import ABCMeta, abstractmethod
from dataclasses import asdict

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import TokenError

from accounts.api import messages
from accounts.api.social_providers import Google, Apple
from accounts.choices import ProviderChoices
from accounts.models import MheroUser

User = get_user_model()


class LogoutSerializer(serializers.Serializer):
    default_error_messages = {"bad_token": messages.INVALID_REFRESH_TOKEN}

    refresh = serializers.CharField(required=True, write_only=True)

    def save(self, **kwargs):
        try:
            token = OutstandingToken.objects.get(token=self.validated_data["refresh"])
            if token.expires_at < timezone.now():
                self.fail("bad_token")
            BlacklistedToken.objects.get_or_create(token=token)

        except (TokenError, OutstandingToken.DoesNotExist):
            pass


class AbstractSerializerMeta(ABCMeta, type(serializers.Serializer)):
    pass


class AbstractAuthSerializer(serializers.Serializer, metaclass=AbstractSerializerMeta):
    """Base class for all authentication serializers."""

    @property
    @abstractmethod
    def provider(self):
        raise NotImplementedError

    def validate(self, attrs):
        """Check whether the user email exists and raise an error when it exists with
        another provider."""
        attrs['email'] = attrs['email'].lower()
        # user = MheroUser.objects.filter(email__iexact=attrs['email']).first()

        # if user and user.provider != self.provider:
        #     provider = ProviderChoices.to_label(user.provider)
        #     raise serializers.ValidationError(
        #       {'detail': f"You have been registered with this email address using {provider}."}
        #     )

        attrs['provider'] = self.provider
        return attrs

    def get_or_create(self):
        """Get or create a user instance."""
        try:
            email = self.validated_data['email']
            return MheroUser.objects.get(email=email, is_deleted=False), False
        except MheroUser.DoesNotExist:
            return MheroUser.objects.create_user(**self.validated_data), True


class AbstractSocialAuthSerializer(AbstractAuthSerializer):
    """Base class for all social authentication serializers."""

    @property
    @abstractmethod
    def provider_class(self):
        raise NotImplementedError

    def validate(self, attrs):
        token_dict = self.provider_class.get_access_token(**attrs)
        user_profile = self.provider_class.get_user_profile(**token_dict)
        user_data = asdict(user_profile)

        # the base validation method should be invoked here since we already have email field
        return super().validate(user_data)


class GoogleAuthSerializer(AbstractSocialAuthSerializer):
    code = serializers.CharField(write_only=True)

    @property
    def provider(self):
        return ProviderChoices.GOOGLE

    @property
    def provider_class(self):
        return Google


class AppleAuthSerializer(AbstractSocialAuthSerializer):
    code = serializers.CharField(write_only=True)

    @property
    def provider(self):
        return ProviderChoices.APPLE

    @property
    def provider_class(self):
        return Apple
