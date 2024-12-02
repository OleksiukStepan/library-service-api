from drf_spectacular.utils import extend_schema


class UserSchema:
    """Schema definitions for user-related operations."""

    create = extend_schema(
        responses={201: "User created successfully", 400: "Bad request"},
        description="Create a new user!",
    )

    manage_user_schema = extend_schema(
        responses={
            200: "User details received/updated successfully",
            401: "Unauthorized",
            400: "Bad request",
        },
        description="Retrieve or update the authenticated user's details.",
    )
