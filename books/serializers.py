from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for converting Book instances to/from JSON."""

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "image"
        )
