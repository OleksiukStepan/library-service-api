from django_filters import rest_framework as filters

from borrowings.models import Borrowing


class BorrowingFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(
        field_name="actual_return_date", lookup_expr="isnull"
    )
    user_id = filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ["is_active", "user_id"]
