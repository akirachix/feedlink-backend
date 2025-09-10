from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, WasteClaim, OrderItem
from .serializers import OrderSerializer, WasteClaimSerializer, OrderItemSerializer
from orders.permissions import OrderPermission,WasteClaimPermission
from django.utils import timezone

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    # def get_queryset(self):
    #     user = self.request.user
        
    #     if user.is_staff or getattr(user, 'role', None) == 'producer':
    #         return Order.objects.all()
     
    #     return Order.objects.filter(user=user)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]  
    
    def get_queryset(self):
        order_id = self.request.query_params.get('order_id')
        if order_id:
            return self.queryset.filter(order_id=order_id)
        return self.queryset


    
    
class WasteClaimViewSet(viewsets.ModelViewSet):
    queryset = WasteClaim.objects.all()
    serializer_class = WasteClaimSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def perform_create(self, serializer):
        serializer.save(claim_time=timezone.now())



