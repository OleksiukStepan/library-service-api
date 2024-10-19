from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from users.serializers import UserSerializer
from payments.models import Payment


User = get_user_model()


class BorrowingSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = ["user", "actual_return_date"]

    def validate_book_inventory(self, book: Book) -> Book:
        if book.inventory <= 0:
            raise ValidationError("This book is currently out of stock")
        return book

    def validate_if_pending_exist(self, user: User) -> None:
        if Borrowing.objects.filter(user=user, payments__status=Payment.Status.PENDING).exists():
            raise ValidationError("You cannot borrow a new book until pending payments are resolved")

    def validate_borrowings_date(self, borrow_date, expected_return_date) -> None:
        today = timezone.now().date()

        if borrow_date < today:
            raise ValidationError("Borrowing cannot be created for past dates")

        if expected_return_date < borrow_date:
            raise ValidationError("Expected return date cannot be earlier than borrow date")

    def create(self, validated_data: dict) -> Borrowing:
        with transaction.atomic():

            book = validated_data["book"]
            self.validate_book_inventory(book)

            user = self.context["request"].user
            self.validate_if_pending_exist(user)

            self.validate_borrowings_date(
                validated_data["borrow_date"],
                validated_data["expected_return_date"]
            )

            book.inventory -= 1
            book.save()
            validated_data["user"] = self.context["request"].user

            return super().create(validated_data)


class BorrowingReturnSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = []

    def return_borrowing(self) -> None:
        self.instance.return_book()


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(slug_field="title", read_only=True)
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)


class BorrowingDetailSerializer(serializers.ModelSerializer):
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
