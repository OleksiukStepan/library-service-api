from django_filters import rest_framework as filters

from borrowings.models import Borrowing


class BorrowingFilter(filters.FilterSet):
    """
        FilterSet for filtering Borrowings.

        Allows filtering Borrowings by their 'is_active' status
        and by the user who borrowed the item.

        Attributes:
            is_active (BooleanFilter): Filter to check if borrowing is active (actual_return_date is null).
            user_id (NumberFilter): Filter to check borrowings by user ID.

        Meta:
            model (Borrowing): The model to filter.
            fields (list): The list of fields available for filtering.
        """
    is_active = filters.BooleanFilter(
        field_name="actual_return_date", lookup_expr="isnull"
    )
    user_id = filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ["is_active", "user_id"]
