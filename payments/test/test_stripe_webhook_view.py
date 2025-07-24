import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from accounts.models import MheroUser
from payments.models import Subscription, SubscriptionPlan, SubscriptionPrice, TransactionHistory
from .test_constants import (
    CHECKOUT_SESSION_COMPLETED_EVENT,
    MOCK_SUBSCRIPTION_DATA,
    INVOICE_PAYMENT_SUCCEEDED_EVENT,
    MOCK_SESSION_LIST_DATA, CUSTOMER_SUBSCRIPTION_DELETED_EVENT,
    CUSTOMER_SUBSCRIPTION_UPDATED_EVENT
)
from ..choices import SubscriptionStatusChoices


class TestStripeWebhookView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MheroUser.objects.create_user(
            id=11,
            email="test@example.com",
            password="testpass"
        )
        cls.plan = SubscriptionPlan.objects.create(
            name="Basic Plan",
            stripe_plan_id="plan_basic_123"
        )
        cls.price = SubscriptionPrice.objects.create(
            subscription_plan=cls.plan,
            name="Basic Plan Price",
            pricing_type="recurring",
            stripe_price_id="price_basic_123",
            price=1000
        )
        cls.webhook_url = reverse("stripe-webhook")

    @patch("stripe.Webhook.construct_event")
    @patch("stripe.Subscription.retrieve")
    def test_checkout_session_completed(self, mock_retrieve_subscription, mock_construct_event):
        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": CHECKOUT_SESSION_COMPLETED_EVENT
        }

        mock_retrieve_subscription.return_value = MOCK_SUBSCRIPTION_DATA

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(CHECKOUT_SESSION_COMPLETED_EVENT),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(Subscription.objects.filter(stripe_subscription_id="sub_123").exists())

    @patch("stripe.Webhook.construct_event")
    def test_invoice_payment_succeeded_after_checkout_session(self, mock_construct_event):
        Subscription.objects.create(
            user=self.user,
            subscription_price=self.price,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatusChoices.ACTIVE,
            start_date=make_aware(datetime.now() - timedelta(days=30)),
            current_period_start=make_aware(datetime.now() - timedelta(days=30)),
            current_period_end=make_aware(datetime.now() + timedelta(days=30))
        )

        mock_construct_event.return_value = {
            "type": "invoice.payment_succeeded",
            "data": INVOICE_PAYMENT_SUCCEEDED_EVENT
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(INVOICE_PAYMENT_SUCCEEDED_EVENT),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(TransactionHistory.objects.all().count(), 1)

    @patch("stripe.Webhook.construct_event")
    @patch("stripe.Subscription.retrieve")
    @patch("stripe.checkout.Session.list")
    def test_invoice_payment_succeeded_before_checkout_session(
            self,
            mock_session_list,
            mock_retrieve_subscription,
            mock_construct_event
    ):
        mock_construct_event.return_value = {
            "type": "invoice.payment_succeeded",
            "data": INVOICE_PAYMENT_SUCCEEDED_EVENT
        }

        mock_retrieve_subscription.return_value = MOCK_SUBSCRIPTION_DATA

        mock_session_list_instance = MagicMock()
        mock_session_list_instance.data = MOCK_SESSION_LIST_DATA["data"]
        mock_session_list.return_value = mock_session_list_instance

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(INVOICE_PAYMENT_SUCCEEDED_EVENT),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(TransactionHistory.objects.all().count(), 1)

    @patch("stripe.Webhook.construct_event")
    def test_customer_subscription_updated(self, mock_construct_event):
        Subscription.objects.create(
            user=self.user,
            subscription_price=self.price,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatusChoices.ACTIVE,
            start_date=make_aware(datetime.now() - timedelta(days=30)),
            current_period_start=make_aware(datetime.now() - timedelta(days=30)),
            current_period_end=make_aware(datetime.now() + timedelta(days=30))
        )

        mock_construct_event.return_value = {
            "type": "customer.subscription.updated",
            "data": CUSTOMER_SUBSCRIPTION_UPDATED_EVENT
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(CUSTOMER_SUBSCRIPTION_UPDATED_EVENT),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch("stripe.Webhook.construct_event")
    def test_customer_subscription_deleted(self, mock_construct_event):
        sub = Subscription.objects.create(
            user=self.user,
            subscription_price=self.price,
            stripe_subscription_id="sub_123",
            status=SubscriptionStatusChoices.ACTIVE,
            start_date=make_aware(datetime.now() - timedelta(days=30)),
            current_period_start=make_aware(datetime.now() - timedelta(days=30)),
            current_period_end=make_aware(datetime.now() + timedelta(days=30))
        )

        mock_construct_event.return_value = {
            "type": "customer.subscription.deleted",
            "data": CUSTOMER_SUBSCRIPTION_DELETED_EVENT
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(CUSTOMER_SUBSCRIPTION_DELETED_EVENT),
            content_type="application/json"
        )

        sub.refresh_from_db()
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(sub.status, SubscriptionStatusChoices.CANCELED)
