from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import MheroUser
from payments.models import TransactionHistory


class TestTransactionHistoryEndpoints(APITestCase):
    def setUp(self):
        self.user = MheroUser.objects.create_user(
            email="test@example.com",
            password="testpass",
            is_active=True
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.transaction_history_path = reverse('transactions')

        self.transaction1 = TransactionHistory.objects.create(
            user=self.user,
            invoice_id="INV001",
            event_type="charge.succeeded",
            amount=100.00,
            status="success",
            event_data={},
        )
        self.transaction2 = TransactionHistory.objects.create(
            user=self.user,
            invoice_id="INV002",
            event_type="charge.failed",
            amount=50.00,
            status="pending",
            event_data={},
        )

    def test_not_authorized_user(self):
        response = self.client.get(
            path=self.transaction_history_path
        )
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_transaction_history_list_authenticated(self):
        response = self.client.get(
            path=self.transaction_history_path,
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}'
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_transaction_history_ordering(self):
        response = self.client.get(
            path=self.transaction_history_path,
            HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}'
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        transaction_ids = [transaction["id"] for transaction in response.data]
        self.assertEqual(transaction_ids, [self.transaction2.id, self.transaction1.id])
