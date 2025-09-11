from rest_framework import serializers

from reviews.models import Review

from inventory.models import Listing


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_id', 
        # 'user_id', 'order_id', 
        'ratings']
        read_only_fields = ['review_id']

    def validate_ratings(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['listing_id', 'status', 'created_at', 'updated_at', 'producer_id']
    def validate(self, data):
        if not data.get('image') and not data.get('image_url'):
            raise serializers.ValidationError("Either image or image_url must be provided.")
        return data