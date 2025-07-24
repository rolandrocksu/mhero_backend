import jwt
import logging
from dataclasses import dataclass
from typing import Dict
from urllib.parse import unquote

import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


@dataclass
class UserProfile:
    email: str
    first_name: str


class Google:
    """The logic is implemented based on OAuth 2.0 industry-standard protocol for authorization."""

    ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    USER_PROFILE_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

    @staticmethod
    def get_access_token(**kwargs) -> Dict[str, str]:
        data = {
            'code': unquote(kwargs['code']),
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.SOCIAL_LOGIN_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post(Google.ACCESS_TOKEN_URL, data=data)
        result = response.json()

        if not response.ok:
            logging.warning(f"Google access token obtain failure {result}.")
            raise ValidationError("Failed to obtain access token from Google.")

        return {'access_token': result['access_token']}

    @staticmethod
    def get_user_profile(**kwargs) -> UserProfile:
        response = requests.get(
            Google.USER_PROFILE_URL,
            params={'access_token': kwargs['access_token']}
        )
        result = response.json()

        if not response.ok:
            logging.warning(f"Google user profile data get failure {result}.")
            raise ValidationError("Failed to obtain user profile data from Google.")

        return UserProfile(email=result['email'], first_name=result['name'])


class Apple:
    """Implements Apple Sign In using OAuth 2.0 with identity token verification."""

    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    USER_INFO_URL = ''  # Apple doesn't provide a separate user info endpoint

    @staticmethod
    def get_access_token(**kwargs) -> Dict[str, str]:
        data = {
            'client_id': settings.APPLE_CLIENT_ID,
            # Apple requires a client secret, usually a JWT
            'client_secret': settings.APPLE_CLIENT_SECRET,
            'code': unquote(kwargs['code']),
            'grant_type': 'authorization_code',
            'redirect_uri': settings.SOCIAL_LOGIN_REDIRECT_URI
        }
        response = requests.post(Apple.ACCESS_TOKEN_URL, data=data)
        result = response.json()

        if not response.ok:
            logging.warning(f"Apple access token obtain failure {result}.")
            raise ValidationError("Failed to obtain access token from Apple.")

        return {
            'access_token': result['access_token'],
            'id_token': result.get('id_token')  # Apple returns an ID token in JWT format
        }

    @staticmethod
    def get_user_profile(**kwargs) -> UserProfile:
        # Apple does not have a user info endpoint; instead, you decode the identity token (JWT)
        id_token = kwargs.get('id_token')
        if not id_token:
            raise ValidationError("Missing ID token from Apple response.")

        # Decode the JWT using the secret or Apple's public keys (use PyJWT for JWT decoding)
        try:
            decoded_token = jwt.decode(
                id_token,
                settings.APPLE_PUBLIC_KEY,
                algorithms=['RS256'],
                audience=settings.APPLE_CLIENT_ID
            )
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')  # Name might be missing

            return UserProfile(email=email, first_name=name)
        except jwt.InvalidTokenError as e:
            logging.warning(f"Apple ID token validation failed: {e}")
            raise ValidationError("Failed to validate ID token from Apple.")
