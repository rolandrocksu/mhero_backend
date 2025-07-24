from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase


class TestMheroUserManager(TestCase):
    user_model = get_user_model()
    email = 'test@gmail.com'
    password = 'Test1234j9'
    phone_number = '+37493377888'

    def setUp(self):
        # Ensure the database is clean before each test
        self.user_model.objects.all().delete()

    def test_create_user_with_email(self):
        user = self.user_model.objects.create_user(
            email=self.email, password=self.password
        )
        self.assertFalse(user.is_superuser)
        self.assertTrue(check_password(self.password, user.password))
        self.assertEqual(user.email, self.email)
        self.assertIsNone(user.phone_number)

    def test_create_user_with_phone_number(self):
        user = self.user_model.objects.create_user(
            phone_number=self.phone_number, password=self.password
        )
        self.assertFalse(user.is_superuser)
        self.assertTrue(check_password(self.password, user.password))
        self.assertEqual(user.phone_number, self.phone_number)
        self.assertIsNone(user.email)

    def test_create_user_with_email_and_phone_number(self):
        user = self.user_model.objects.create_user(
            email=self.email, phone_number=self.phone_number, password=self.password
        )
        self.assertFalse(user.is_superuser)
        self.assertTrue(check_password(self.password, user.password))
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.phone_number, self.phone_number)

    def test_create_superuser_with_email(self):
        super_user = self.user_model.objects.create_superuser(
            email=self.email, password=self.password
        )
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(check_password(self.password, super_user.password))
        self.assertEqual(super_user.email, self.email)
        self.assertIsNone(super_user.phone_number)

    def test_unique_phone_number(self):
        self.user_model.objects.create_user(
            phone_number=self.phone_number, password=self.password
        )
        with self.assertRaises(Exception) as context:
            self.user_model.objects.create_user(
                phone_number=self.phone_number, password="AnotherPassword"
            )
        self.assertIn("already exists.", str(context.exception))

    def test_blank_email(self):
        user = self.user_model.objects.create_user(
            email='', phone_number=self.phone_number, password=self.password
        )
        self.assertIsNone(user.email)
        self.assertEqual(user.phone_number, self.phone_number)

    def test_blank_phone_number(self):
        user = self.user_model.objects.create_user(
            email=self.email, phone_number='', password=self.password
        )
        self.assertIsNone(user.phone_number)
        self.assertEqual(user.email, self.email)
