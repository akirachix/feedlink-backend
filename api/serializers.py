from rest_framework import serializers
from payment.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            'transaction_id',
            'mpesa_receipt_number',
            'checkout_request_id',
            'merchant_request_id',
            'result_code',
            'result_desc',
            'phone_number',
            'created_at'

        )

class USSDPUSHSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    account_reference = serializers.CharField()
    transaction_desc = serializers.CharField()