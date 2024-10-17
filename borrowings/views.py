from rest_framework.viewsets import ModelViewSet

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)


class BorrowingViewSet(ModelViewSet):

    def get_queryset(self):
        if self.action == "list":
            return (
                Borrowing.objects.select_related("user").prefetch_related("book")
            )
        elif self.action == "retrieve":
            return Borrowing.objects.select_related("user", "book")
        return Borrowing.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
