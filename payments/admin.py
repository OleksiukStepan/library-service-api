from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "type",
        "borrowing",
        "session_id",
        "money_to_pay",
    )
    list_filter = (
        "status",
        "type",
        "borrowing",
    )
