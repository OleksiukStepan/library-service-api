from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer
from django.utils.decorators import method_decorator
from users.schemas import UserSchema

User = get_user_model()


@method_decorator(UserSchema.create, name="post")
class CreateUserView(generics.CreateAPIView):
    """
    API view for creating a new user.
    Uses the UserSerializer for validation and creation.
    No authentication or permission is required.
    """

    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()


@method_decorator(UserSchema.manage_user_schema, name="get")
@method_decorator(UserSchema.manage_user_schema, name="put")
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving or updating the authenticated user's details.
    Requires JWT authentication.
    """

    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = ()

    def get_object(self):
        """Returns the current authenticated user."""

        return self.request.user
