from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(max_length=10, choices=Status.choices)
    type = models.CharField(max_length=10, choices=Type.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.TextField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    def __str__(self):
        return f"{self.type} for {self.borrowing.book.title} ({self.status})"
