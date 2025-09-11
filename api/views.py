from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from reviews.models import Review          
from .serializers import ReviewSerializer  

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer