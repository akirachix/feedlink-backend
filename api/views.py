from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from django.utils import timezone


# Create your views here.
from rest_framework import viewsets
from orders.models import Order, WasteClaim
from .serializers import OrderSerializer, WasteClaimSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class WasteClaimViewSet(viewsets.ModelViewSet):
    queryset = WasteClaim.objects.all()
    serializer_class = WasteClaimSerializer

    def perform_create(self, serializer):
        serializer.save(claim_time=timezone.now())

