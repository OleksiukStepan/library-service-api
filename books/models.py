import os
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


def books_image_file_path(instance: "Book", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/books/", filename)

def validate_image_size(image):
    max_size_mb = 10

    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image size can't exceed {max_size_mb} MB.")

class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=CoverType.choices)
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    image = models.ImageField(
        upload_to=books_image_file_path,
        null=True,
        blank=True,
        validators=[validate_image_size],
    )

    def __str__(self):
        return f"{self.title} by {self.author}"
