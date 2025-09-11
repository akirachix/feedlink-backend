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
from rest_framework import generics, status

import csv
from io import TextIOWrapper
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from location.models import UserLocation
from user.models import User

from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    ForgotPasswordSerializer,
    VerifyCodeSerializer,
    ResetPasswordSerializer,
    ListingSerializer
)


otp_storage = {}

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
   

class UserSignupAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
      
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })



class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(1000, 9999))
        otp_storage[email] = otp  

        send_mail(
            'Your OTP for password reset',
            f'Your OTP is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"detail": "OTP sent to your email."})

class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        if otp_storage.get(email) != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "OTP verified."})
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        otp_storage.pop(email, None) 
        return Response({"detail": "Password reset successful."})

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
        
