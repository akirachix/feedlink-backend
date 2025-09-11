from rest_framework import serializers
from orders.models import Order, OrderItem, WasteClaim
from inventory.models import Listing



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['price'] 

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_id', 'order_date', 'total_amount', 'pin'] 

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(total_amount=0, **validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        order.update_total_amount()
        return order

    def update(self, instance, validated_data):
    
        allowed = ['order_status', 'payment_status']
        for field in list(validated_data.keys()):
            if field not in allowed:
                validated_data.pop(field)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class WasteClaimSerializer(serializers.ModelSerializer):
    listing_id = serializers.IntegerField(source='listing.listing_id', read_only=True)

    
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(product_type='inedible'),
        source='listing'
    )
    
    class Meta:
        model = WasteClaim
        fields =  ['waste_id', 'listing_id', 'claim_time', 'claim_status', 'pin', 'created_at', 'updated_at']
        read_only_fields = ['waste_id','listing_id', 'pin', 'created_at', 'updated_at']

    


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['listing_id', 'status', 'created_at', 'updated_at', 'producer_id']

    def validate(self, data):
    
        if not data.get('image') and not data.get('image_url'):
            raise serializers.ValidationError("Either image or image_url must be provided.")
        return data

