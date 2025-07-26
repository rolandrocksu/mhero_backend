
from django.contrib.auth.models import UserManager


class MheroUserManager(UserManager):
    """Overriding default UserManager's behavior to omit username field."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email")

        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, phone_number, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email=email, password=password, **extra_fields)
