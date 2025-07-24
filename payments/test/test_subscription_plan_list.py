from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from accounts.models import MheroUser
from payments.models import SubscriptionPlan


class TestSubscriptionPlanListView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MheroUser.objects.create_user(
            phone_number="+37493377888",
            password="testpass",
            is_active=True
        )
        cls.refresh = RefreshToken.for_user(cls.user)
        cls.plan1 = SubscriptionPlan.objects.create(
            name="Basic Plan",
            stripe_plan_id="plan_basic_123"
        )
        cls.plan2 = SubscriptionPlan.objects.create(
            name="Premium Plan",
            stripe_plan_id="plan_premium_456"
        )
        cls.subscription_plan_list_url = reverse("subscription_plans")

    def test_not_authorized_user(self):
        response = self.client.get(
            path=self.subscription_plan_list_url
        )
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_subscription_plan_list_success(self):
        response = self.client.get(
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}',
            path=self.subscription_plan_list_url
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_empty_subscription_plan_list(self):
        SubscriptionPlan.objects.all().delete()
        response = self.client.get(
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}',
            path=self.subscription_plan_list_url
        )
        self.assertEqual(response.json(), [])
