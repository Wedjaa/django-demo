from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class DjangoUserManager(BaseUserManager):
    use_in_migration = True

    def _create_user(self, username, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError("The username must be set")
        username = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(extra_fields.get("password", None))
        user.save(using=self._db)
        return user

    def create_user(self, username, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("roles", [])
        return self._create_user(username, **extra_fields)

    def create_superuser(self, username, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, **extra_fields)


class DjangoUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    roles = models.JSONField(default=list)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    manager = DjangoUserManager()
    objects = manager
