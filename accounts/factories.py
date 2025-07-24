import factory
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from factory import django

user = get_user_model()


class UserFactory(django.DjangoModelFactory):
    """Create test user."""

    class Meta:
        model = user

    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_superuser = False
    last_login = now()
    password = 'password'
