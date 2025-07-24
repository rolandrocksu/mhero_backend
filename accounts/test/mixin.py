from django.urls import reverse
from django.utils.timezone import now

from accounts.factories import UserFactory


class ViewsTestCaseMixin:

    def create_user(self, email: str, password: str, is_admin: bool):
        if is_admin:
            test_user = UserFactory.create(email=email, is_superuser=True)
        else:
            test_user = UserFactory.create(email=email)
        test_user.set_password(password)
        test_user.last_login = now()
        test_user.save()
        response = self.client.post(reverse('login'), {"email": email, "password": password})
        return test_user, response.json().get('access'), response.json().get('refresh')

    def create_employee(self, email, password):
        return self.create_user(email, password, False)

    def create_admin(self, email, password):
        return self.create_user(email, password, True)
