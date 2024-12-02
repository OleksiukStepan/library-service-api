from datetime import datetime

from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.serializers import PaymentUserSerializer
from users.serializers import UserSerializer
from payments.models import Payment


User = get_user_model()


class BorrowingSerializer(serializers.ModelSerializer):
    """
    Serializer for Borrowing model.

    Serializes borrowing details, including related book and user information.
    Ensures that book inventory is updated and validations are performed for
    stock availability and pending payments.

    """

    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    payments = PaymentUserSerializer(
        many=True,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        ]
        read_only_fields = ["user", "actual_return_date"]

    def validate_book_inventory(self, book: Book) -> Book:
        """
        Validates if the book is in stock.
        """
        if book.inventory <= 0:
            raise ValidationError("This book is currently out of stock")
        return book

    def validate_if_pending_exist(self, user: User) -> None:
        """
        Validates if the user has pending payments.
        """
        if Borrowing.objects.filter(
            user=user, payments__status=Payment.Status.PENDING
        ).exists():
            raise ValidationError(
                "You cannot borrow a new book until "
                "pending payments are resolved"
            )

    def validate_borrowings_date(
            self,
            borrow_date: datetime,
            expected_return_date: datetime
    ) -> None:
        """
        Validates the dates for the borrowing.
        """
        today = timezone.now().date()

        if borrow_date < today:
            raise ValidationError("Borrowing cannot be created for past dates")

        if expected_return_date < borrow_date:
            raise ValidationError(
                "Expected return date cannot be earlier than borrow date"
            )

    def create(self, validated_data: dict) -> Borrowing:
        """
        Creates a new borrowing instance with proper validations.
        """

        with transaction.atomic():
            book = validated_data["book"]
            user = self.context["request"].user

            self.validate_book_inventory(book)
            self.validate_if_pending_exist(user)
            self.validate_borrowings_date(
                validated_data["borrow_date"],
                validated_data["expected_return_date"]
            )

            book.inventory -= 1
            book.save()
            validated_data["user"] = user

            return super().create(validated_data)


class BorrowingReturnSerializer(BorrowingSerializer):
    """
    Serializer for returning a borrowing.

    Handles the logic for returning a borrowed book.
    """

    class Meta:
        model = Borrowing
        fields = []

    def return_borrowing(self) -> None:
        self.instance.return_book()


class BorrowingListSerializer(BorrowingSerializer):
    """
    Serializer for listing borrowings.

    Lists borrowings with slug fields for book title and user email.
    """

    book = serializers.SlugRelatedField(slug_field="title", read_only=True)
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    """
    Serializer for detailed view of a borrowing.

    Provides detailed information about a borrowing, including
    serialized book and user details.
    """

    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta(BorrowingSerializer.Meta):
        read_only_fields = [
            "user",
            "actual_return_date",
            "expected_return_date",
            "borrow_date",
            "book",
        ]
