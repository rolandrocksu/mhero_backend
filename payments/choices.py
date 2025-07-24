from django.db.models import TextChoices


class SubscriptionStatusChoices(TextChoices):
    ACTIVE = 'active', 'Active'
    PAST_DUE = 'past_due', 'Past Due'
    CANCELED = 'canceled', 'Canceled'
    EXPIRED = 'expired', 'Expired'
