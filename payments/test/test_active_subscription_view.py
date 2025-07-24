from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from accounts.models import MheroUser
from payments.choices import SubscriptionStatusChoices
from payments.models import Subscription, SubscriptionPlan, SubscriptionPrice


class TestActiveSubscriptionEndpoints(APITestCase):
    def setUp(self):
        self.user = MheroUser.objects.create_user(
            email="test@example.com",
            password="testpass",
            is_active=True
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.active_subscription_path = reverse('active-subscription')

        self.plan = SubscriptionPlan.objects.create(name="Basic Plan",
                                                    stripe_plan_id="plan_basic_123")
        self.price = SubscriptionPrice.objects.create(
            subscription_plan=self.plan,
            name="Basic Price",
            pricing_type="recurring",
            stripe_price_id="price_basic_123",
            price=1000
        )

    def test_not_authorized_user(self):
        response = self.client.get(
            path=self.active_subscription_path
        )
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_no_active_subscription(self):
        response = self.client.get(
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}',
            path=self.active_subscription_path
        )
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_active_subscription_found(self):
        Subscription.objects.create(
            user=self.user,
            subscription_price=self.price,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatusChoices.ACTIVE,
            start_date=make_aware(datetime.now() - timedelta(days=30)),
            current_period_start=make_aware(datetime.now() - timedelta(days=30)),
            current_period_end=make_aware(datetime.now() + timedelta(days=30))
        )
        response = self.client.get(
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}',
            path=self.active_subscription_path
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_expired_subscription(self):
        Subscription.objects.create(
            user=self.user,
            subscription_price=self.price,
            stripe_subscription_id="sub_expired_123",
            status=SubscriptionStatusChoices.CANCELED,
            start_date=make_aware(datetime.now() - timedelta(days=60)),
            current_period_start=make_aware(datetime.now() - timedelta(days=60)),
            current_period_end=make_aware(datetime.now() - timedelta(days=30))
        )

        response = self.client.get(
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}',
            path=self.active_subscription_path
        )
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
