from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class IsAdminOrIfAuthenticatedPostAndReadOnly(BasePermission):
    """
    Custom permission to allow read-only access to authenticated users
    and full access to admin users.

    Authenticated users can perform safe methods (GET, HEAD, OPTIONS)
    and POST requests, but not other modifications (PUT, PATCH, DELETE).
    Admin users have full access to all methods.

    Methods:
        has_permission(self, request, view): Checks if the request
        should be permitted.
    """

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        return bool(
            (
                request.method in (SAFE_METHODS + ("POST",))
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
