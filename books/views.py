from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from books.filters import BookFilter
from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """API viewset for managing books. Provides CRUD operations and filtering."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = BookFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by book title (ex. ?title=Harry Potter)",
            ),
            OpenApiParameter(
                "author",
                type=OpenApiTypes.STR,
                description="Filter by author name (ex. ?author=Tolkien)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
