from rest_framework import viewsets,  mixins
from rest_framework.response import Response
from rest_framework import status
from reviews.models import Review          
from .serializers import ReviewSerializer  

class ReviewViewSet(
    mixins.ListModelMixin,      
    mixins.CreateModelMixin,    
    viewsets.GenericViewSet
):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer