from rest_framework import serializers

from payments.models import Payment


class PaymentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "money_to_pay",
            "session_url",
        )


class PaymentStaffSerializer(PaymentUserSerializer):
    class Meta(PaymentUserSerializer.Meta):
        fields = PaymentUserSerializer.Meta.fields + (
            "borrowing",
            "session_id",
        )
