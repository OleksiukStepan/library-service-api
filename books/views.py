from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from books.models import Book
from books.ordering import BookOrdering
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer
from books.filters import BookFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class BookViewSet(viewsets.ModelViewSet):
    """API viewset for managing books. Provides CRUD operations and filtering."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend]
    ordering_fields = ["title", "author"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                description="Filter by book title (ex. ?title=Harry Potter)",
            ),
            OpenApiParameter(
                name="author",
                type=OpenApiTypes.STR,
                description="Filter by author name (ex. ?author=Tolkien)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                description=(
                        "Specify fields to order the results by. "
                        "Available fields are title and author. "
                        "Prefix with - for descending order. "
                        "Multiple fields can be separated by commas "
                        "(ex. ?ordering=title or ?ordering=-author)"
                ),
            ),
        ]
    )

    def list(self, request, *args, **kwargs):
        ordering_fields = BookOrdering.get_ordering_fields(request, fields=self.ordering_fields)
        self.queryset = self.queryset.order_by(*ordering_fields)
        return super().list(request, *args, **kwargs)
