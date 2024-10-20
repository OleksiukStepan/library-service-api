from django.contrib.auth.models import BaseUserManager, AbstractUser


class UserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier."""

    use_in_migrations = True

    def _create_user(
            self, email: str, password: str, **extra_fields
    ) -> AbstractUser:
        """Creates and saves a User with the given email and password."""

        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self,
            email: str,
            password: str,
            **extra_fields
    ) -> AbstractUser:
        """Creates and saves a regular user (non-superuser)."""

        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str, **extra_fields
    ) -> AbstractUser:
        """Creates and saves a superuser with required permissions."""

        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self._create_user(email, password, **extra_fields)
