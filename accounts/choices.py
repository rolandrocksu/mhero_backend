from lib.model_fields import CustomIntegerChoices
from django.db.models import TextChoices


class NotificationTransportChoices(CustomIntegerChoices):
    email = (1, "email")
    sms = (2, "sms")


class ProviderChoices(CustomIntegerChoices):
    EMAIL = 1, 'Email'
    GOOGLE = 2, 'Google'
    AMAZON = 3, 'Amazon'
    APPLE = 4, 'Apple'
    PHONE_NUMBER = 5, 'PhoneNumber'


class AccountDeletionChoices(TextChoices):
    REQUESTED = 'Requested'
    DONE = 'Done'
