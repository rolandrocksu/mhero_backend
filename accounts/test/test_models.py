from django.test import TestCase

from accounts.factories import UserFactory


class UserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory()

    def test_user_str(self):
        self.assertEqual(str(self.user), self.user.email)

    def test_user_full_name(self):
        self.assertEqual(
            self.user.full_name,
            " ".join([self.user.first_name, self.user.last_name])
        )
