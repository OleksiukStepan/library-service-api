from rest_framework.serializers import Serializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend

from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)
from borrowings.filters import BorrowingFilter
from notifications.tasks import send_telegram_message
from payments.stripe_helpers import create_stripe_session


class BorrowingViewSet(ModelViewSet):
    """
    ViewSet for managing book borrowings.

    Allows access only to authenticated users.
    Admin users can see all borrowings, while regular users can only see their own.
    Supports filtering by `is_active` and `user_id` parameters.
    """
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    filterset_class = BorrowingFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self) -> QuerySet:
        """
        Returns the queryset for borrowings.

        If the user is an admin, returns all borrowings.
        Regular users only see their own borrowings.
        """
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.select_related("user", "book")
        return (
            Borrowing.objects.select_related("user", "book")
            .filter(user=user)
        )

    def get_serializer_class(self) -> type(Serializer):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer: ModelSerializer) -> None:
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
        create_stripe_session(borrowing, self.request)
        send_telegram_message(message)

    @action(detail=True, methods=["POST"])
    def return_borrowing(self, request: Request, pk: str = None) -> Response:
        borrowing = self.get_object()
        serializer = self.get_serializer(
            instance=borrowing, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.return_borrowing()
            create_stripe_session(borrowing, request)
            return Response({"message": "The book was successfully returned"})
        except ValidationError:
            return Response(
                {"error": "This book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST
            )
