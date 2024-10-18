from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.db.models import QuerySet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from borrowings.filters import BorrowingFilter
from notifications.tasks import send_telegram_message


class BorrowingViewSet(ModelViewSet):
    """
    ViewSet for managing book borrowings.

    Allows access only to authenticated users.
    Admin users can see all borrowings, while regular users can only see their own.
    Supports filtering by `is_active` and `user_id` parameters.
    """
    permission_classes = (IsAuthenticated,)
    filterset_class = BorrowingFilter

    def get_queryset(self) -> QuerySet:
        """
        Returns the queryset for borrowings.

        If the user is an admin, returns all borrowings.
        Regular users only see their own borrowings.
        """
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.select_related("user", "book")
        return Borrowing.objects.select_related("user", "book").filter(user=user)

    def get_serializer_class(self) -> type(Serializer):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        """
        Saves a new borrowing, setting the user to the currently authenticated user.
        Sends a notification to Telegram about the new borrowing.
        """
        borrowing = serializer.save(user=self.request.user)
        message = (
            f"New borrowing created (ID: {borrowing.id}):\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Due Date: {borrowing.expected_return_date}"
        )
        send_telegram_message(message)
