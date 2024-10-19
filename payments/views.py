import stripe
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.tasks import send_telegram_message
from payments.models import Payment
from payments.serializers import PaymentUserSerializer, PaymentStaffSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return Payment.objects.filter(borrowing__user=user)
        return Payment.objects.all()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff:
            return PaymentStaffSerializer
        return PaymentUserSerializer


class PaymentSuccessView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        payment = get_object_or_404(Payment, session_id=session_id)
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            payment.status = Payment.Status.PAID
            payment.save()
            message = (
                f"{payment.get_type_display()} for borrowing "
                f"(ID: {payment.borrowing.id}):\n"
                f"Amount: $ {payment.money_to_pay}\n"
                f"User: {payment.borrowing.user.email}"
            )
            send_telegram_message(message)

            return Response({"message": "Payment successful"}, status=200)
        else:
            return Response({"message": "Payment not completed"}, status=400)


class PaymentCancelView(APIView):
    def get(self, request):
        return Response(
            {"message": "Payment was cancelled. You can try again within 24 hours."},
            status=200,
        )
