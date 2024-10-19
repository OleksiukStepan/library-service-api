from django_filters import rest_framework as filters
from books.models import Book


class BookFilter(filters.FilterSet):
    """Filter class for filtering books by title and author."""

    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    author = filters.CharFilter(field_name="author", lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ["title", "author"]
