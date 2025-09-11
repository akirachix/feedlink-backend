from rest_framework import serializers

from reviews.models import Review

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
