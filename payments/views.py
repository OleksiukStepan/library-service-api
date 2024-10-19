import stripe
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers import PaymentUserSerializer, PaymentStaffSerializer


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for retrieving payment information.

    This viewset provides read-only access to Payment objects.
    Regular users can only view their own payments, while staff
    users can view all payments in the system.
    - Staff users receive more detailed information
    - Regular users receive limited information
    """
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
    """
    Handle successful Stripe payment confirmations.

    This view retrieves a payment session using the provided session_id
    and checks the payment status with Stripe. If the payment is successful
    (status is 'paid'), the corresponding Payment object in the database is
    updated to reflect the successful status. Otherwise, an error response
    is returned.
    """
    def get(self, request):
        session_id = request.query_params.get("session_id")
        payment = get_object_or_404(Payment, session_id=session_id)
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            payment.status = Payment.Status.PAID
            payment.save()

            return Response(
                {"message": "Payment successful"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Payment not completed"}, status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCancelView(APIView):
    """
    Handle payment cancellations.

    This view returns a message to inform the user that their payment was cancelled.
    It indicates that the user can attempt to complete the payment again within 24 hours.

    Responses:
    - 200 OK: Confirms that the payment was cancelled and provides a message.
    """
    def get(self, request):
        return Response(
            {"message": "Payment was cancelled. You can try again within 24 hours."},
            status=status.HTTP_200_OK,
        )
