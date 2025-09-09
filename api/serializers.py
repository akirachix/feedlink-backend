from rest_framework import serializers
from orders.models import Order, WasteClaim

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'order_id', 'order_date', 'order_status', 'payment_status',
            'total_amount', 'pin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_id', 'pin', 'order_date', 'created_at', 'updated_at']

class WasteClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteClaim
        fields = [
            'waste_id', 'claim_status', 'claim_time', 'pickup_window_end',
            'pin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['waste_id', 'pin', 'claim_time', 'created_at', 'updated_at']


