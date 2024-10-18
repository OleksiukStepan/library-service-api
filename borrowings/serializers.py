from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from users.serializers import UserSerializer
from books.models import Book


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
        read_only_fields = ["user"]

    def validate_book_inventory(self, book: Book) -> Book:
        if book.inventory <= 0:
            raise ValidationError("This book is currently out of stock")
        return book

    def create(self, validated_data: dict) -> Borrowing:
        with transaction.atomic():
            book = validated_data["book"]
            self.validate_book_inventory(book)
            book.inventory -= 1
            book.save()
            validated_data["user"] = self.context["request"].user

            return super().create(validated_data)


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(slug_field="title", read_only=True)
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
