from django.urls import path
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet, PaymentSuccessView, PaymentCancelView
)

app_name = "payments"

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]

urlpatterns += router.urls
