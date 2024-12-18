from rest_framework.serializers import Serializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrIfAuthenticatedPostAndReadOnly
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
    Admin users can see all borrowings,
    while regular users can only see their own.
    Supports filtering by `is_active` and `user_id` parameters.
    """

    permission_classes = [IsAdminOrIfAuthenticatedPostAndReadOnly]
    filterset_class = BorrowingFilter

    @extend_schema(
        summary="List borrowings",
        description="List of borrowings. Admins see all, "
                    "regular users see their own borrowings only.",
        responses={200: BorrowingListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID",
                required=False,
                type=int,
            ),
        ],
    )
    def list(self, request: Request, *args, **kwargs):
        """List borrowings with optional filters."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve borrowing",
        description="Retrieve details of a single borrowing by its ID.",
        responses={200: BorrowingDetailSerializer},
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Borrowing:
        """Retrieve a single borrowing by ID."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create new borrowing",
        description="Create a new borrowing for a book. "
                    "Sends a notification to Telegram and "
                    "creates a Stripe session.",
        request=BorrowingSerializer,
        responses={201: BorrowingSerializer},
    )
    def create(self, request: Request, *args, **kwargs):
        """Create a new borrowing."""
        return super().create(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """
        Returns the queryset for borrowings.

        If the user is an admin, returns all borrowings.
        Regular users only see their own borrowings.
        """
        user = self.request.user
        queryset = Borrowing.objects.select_related("user", "book")
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)

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
        Saves a new borrowing, setting the user to
        the currently authenticated user.
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

    @extend_schema(
        summary="Return borrowing",
        description="Mark a borrowing as returned. "
                    "This action is available only to admin users.",
        request=BorrowingReturnSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description="The book was successfully returned"
            ),
            400: OpenApiResponse(
                response=dict,
                description="This book has already been returned"
            ),
        },
    )
    @action(detail=True, methods=["POST"], permission_classes=[IsAdminUser])
    def return_borrowing(self, request: Request, pk: str = None) -> Response:
        """
        Action to mark a borrowing as returned.

        This action is restricted to admin users and marks
        the selected borrowing as returned by setting the `actual_return_date`.
        If the borrowing has already been returned,
        a validation error is raised.

        Steps:
        1. Retrieve the borrowing instance using the primary key (pk).
        2. Validate the data using the serializer.
        3. Attempt to mark the borrowing as returned.
        4. Create a Stripe session for the returned borrowing.
        5. Return a success response if the book was successfully returned.
        6. Return an error response if the book has already been returned.
        """
        borrowing = self.get_object()
        serializer = self.get_serializer(instance=borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.return_borrowing()
            create_stripe_session(borrowing, request)
            return Response({"message": "The book was successfully returned"})
        except ValidationError:
            return Response(
                {"error": "This book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )
