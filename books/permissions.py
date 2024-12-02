from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class IsAdminOrReadOnly(BasePermission):
    """Custom permission to allow read-only access for unauthenticated users
    and full access for admin users."""

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        """Check if the request is safe or if the user is an admin."""
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
