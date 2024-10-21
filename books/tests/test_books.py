import io
from decimal import Decimal

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book
from books.serializers import BookSerializer
from django.urls import reverse

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id: int) -> str:
    """Returns the detail URL for a book."""
    return reverse("books:book-detail", args=[book_id])


class PublicBookApiTests(TestCase):
    """Tests for public access to the book API."""

    def setUp(self) -> None:
        """Set up the API client for test."""
        self.client = APIClient()

    def test_filter_books_by_title(self) -> None:
        """Test filtering books by title."""
        book1 = Book.objects.create(
            title="Harry Potter",
            author="J.K. Rowling",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("1.50"),
        )
        book2 = Book.objects.create(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("2.00"),
        )

        res = self.client.get(BOOKS_URL, {"title": "harry"})

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_filter_books_by_author(self) -> None:
        """Test filtering books by author."""
        book1 = Book.objects.create(
            title="Harry Potter",
            author="J.K. Rowling",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("1.50"),
        )
        book2 = Book.objects.create(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("2.00"),
        )

        res = self.client.get(BOOKS_URL, {"author": "tolkien"})

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)

        self.assertNotIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])

    def test_retrieve_books_ordered_by_title(self) -> None:
        """Test retrieving a list of books ordered by title."""
        Book.objects.create(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("2.00"),
        )
        Book.objects.create(
            title="Harry Potter",
            author="J.K. Rowling",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("1.50"),
        )

        res = self.client.get(f"{BOOKS_URL}?ordering=title")

        books = Book.objects.all().order_by("title")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.data["results"], serializer.data)

    def test_create_book_unauthorized(self) -> None:
        """Test creating a book when unauthorized."""
        payload = {
            "title": "Unauthorized Book",
            "author": "Unauthorized Author",
            "cover": Book.CoverType.HARD,
            "inventory": 5,
            "daily_fee": Decimal("1.50"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(
            Book.objects.filter(title="Unauthorized Book").exists()
        )


class AdminBookApiTests(TestCase):
    """Tests for admin access to the book API."""

    def setUp(self) -> None:
        """Set up the API client and admin user for tests."""
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.admin_user)
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.HARD,
            inventory=10,
            daily_fee=Decimal("2.00"),
        )
        self.book_url = f"/api/books/{self.book.id}/"

    def tearDown(self) -> None:
        """Clean up after tests."""
        books = Book.objects.all()
        for book in books:
            if book.image:
                book.image.delete(save=False)

    def test_create_book(self) -> None:
        """Test creating a new book."""
        payload = {
            "title": "New Book",
            "author": "Author Name",
            "cover": Book.CoverType.HARD,
            "inventory": 20,
            "daily_fee": Decimal("3.00"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(getattr(book, key), payload[key])

    def test_create_book_with_image(self) -> None:
        """Test creating a new book with an image."""
        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image_file = io.BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)

        payload = {
            "title": "New Book with Image",
            "author": "Author Name",
            "cover": Book.CoverType.HARD,
            "inventory": 20,
            "daily_fee": Decimal("3.00"),
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=image_file.read(),
                content_type="image/jpeg",
            ),
        }

        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_book(self) -> None:
        """Test deleting a book."""
        response = self.client.get(self.book_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(self.book_url)
        self.assertEqual(
            delete_response.status_code, status.HTTP_204_NO_CONTENT
        )

        response_after_delete = self.client.get(self.book_url)
        self.assertEqual(
            response_after_delete.status_code, status.HTTP_404_NOT_FOUND
        )
