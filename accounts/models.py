from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date
from accounts.choices import ProviderChoices, AccountDeletionChoices
from accounts.managers import MheroUserManager


class MheroUser(AbstractUser):
    username = None
    date_joined = None

    email = models.EmailField(unique=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.IntegerField(
        choices=ProviderChoices.choices,
        blank=True,
        null=True,
        default=None
    )
    is_deleted = models.BooleanField(default=False)

    objects = MheroUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def tokens_used_today(self):
        usage = self.daily_token_usage.filter(date=date.today()).first()
        return usage.tokens_used if usage else 0

    @property
    def remaining_tokens_today(self):
        limit = settings.MAX_DAILY_TOKENS
        return max(limit - self.tokens_used_today, 0)

    @property
    def valid_access_tokens(self):
        valid_tokens = []
        all_tokens = self.outstandingtoken_set.all()

        for token_obj in all_tokens:
            try:
                token = token_obj.token
                RefreshToken(token)
                valid_tokens.append(token_obj)
            except TokenError:
                pass

        return valid_tokens


class AccountDeletion(models.Model):

    user = models.ForeignKey(
        MheroUser,
        on_delete=models.CASCADE,
        related_name='deletion_requests'
    )
    identifier = models.CharField(max_length=50)
    request_date = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        max_length=20,
        choices=AccountDeletionChoices,
        default=AccountDeletionChoices.REQUESTED
    )
    reason = models.TextField()

    def __str__(self):
        return f"Deletion Request - {self.user.email} - {self.state}"
