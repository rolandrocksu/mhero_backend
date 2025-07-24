from django.db import models

from accounts.models import MheroUser
from payments.choices import SubscriptionStatusChoices


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    stripe_plan_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SubscriptionPrice(models.Model):
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='subscription_prices'
    )
    name = models.CharField(max_length=100)
    pricing_type = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField()


class Subscription(models.Model):
    user = models.ForeignKey(
        MheroUser,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    subscription_price = models.ForeignKey(SubscriptionPrice, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatusChoices.choices,
        default=SubscriptionStatusChoices.ACTIVE,
    )
    final_price = models.IntegerField(null=True, blank=True)
    invoice_id = models.CharField(max_length=255, null=True, blank=True)

    start_date = models.DateTimeField()
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    event_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - ({self.status})"

    @classmethod
    def get_active_subscription(cls, user):
        return cls.objects.filter(
            user=user, status=SubscriptionStatusChoices.ACTIVE
        ).order_by('-current_period_end').first()


class TransactionHistory(models.Model):
    user = models.ForeignKey(
        MheroUser,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    invoice_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=50)
    amount = models.IntegerField()
    status = models.CharField(max_length=50)
    event_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.event_type} - {self.amount}"
