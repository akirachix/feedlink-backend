from rest_framework import serializers
from inventory.models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['listing_id', 'status', 'created_at', 'updated_at', 'producer_id']

    def validate(self, data):
    
        if not data.get('image') and not data.get('image_url'):
            raise serializers.ValidationError("Either image or image_url must be provided.")
        return data
