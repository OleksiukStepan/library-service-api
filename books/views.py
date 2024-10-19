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
