from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from users.models import User
from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def return_book(self) -> None:
        if self.actual_return_date:
            raise ValidationError("This book has already been returned")
        self.actual_return_date = timezone.now().date()
        self.book.inventory += 1
        self.book.save()
        self.save()

    def __str__(self):
        return f"Borrowing of {self.book.title} by {self.user.email}"
