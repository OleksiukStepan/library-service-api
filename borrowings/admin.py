from django.contrib import admin

from borrowings.models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book",
        "user",
    )
    list_filter = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book",
        "user",
    )
    search_fields = ("book__title", "user__email")