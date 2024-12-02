from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model, handling creation and updates."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
        )
        read_only_fields = (
            "id",
            "is_staff",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data: dict) -> User:
        """Create and return a new user with encrypted password."""

        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        return user

    def update(self, instance: User, validated_data: dict) -> User:
        """
        Update user details, set password if provided, and return the user.
        """

        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user
