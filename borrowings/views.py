from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from borrowings.filters import BorrowingFilter
from notifications.tasks import send_telegram_message


class BorrowingViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filterset_class = BorrowingFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.select_related("user", "book")
        return Borrowing.objects.select_related("user", "book").filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        message = (
            f"New borrowing created (ID: {borrowing.id}):\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}\n"
            f"Due Date: {borrowing.expected_return_date}"
        )
        send_telegram_message(message)
