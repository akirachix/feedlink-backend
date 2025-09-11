from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, WasteClaim, OrderItem
from .serializers import OrderSerializer, WasteClaimSerializer, OrderItemSerializer, ListingSerializer
from orders.permissions import OrderPermission,WasteClaimPermission
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from inventory.models import Listing

import csv
from io import TextIOWrapper

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

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

    def get_queryset(self):
        return WasteClaim.objects.filter(listing__product_type='inedible') \
                                 .select_related('listing') 
                                 

    def perform_create(self, serializer):
        serializer.save(claim_time=timezone.now())





class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    
class ListingCSVUploadView(APIView):
    
    def post(self, request):
        file = request.FILES.get('csv_file')
        if not file:
            return Response({"error": "No CSV file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
        listings_created = []
        errors = []

        for row in reader:
            serializer = ListingSerializer(data=row)
            if serializer.is_valid():
                instance = serializer.save(status='available', upload_method='csv')
                listings_created.append(serializer.data)
            else:
                errors.append({
                    "row": row,
                    "errors": serializer.errors
                })

        if errors:
            return Response({
                "created": listings_created,
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                "listings": listings_created
            }, status=status.HTTP_201_CREATED)
        
