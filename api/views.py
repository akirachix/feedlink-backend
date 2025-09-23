import random
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
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from location.models import UserLocation
from user.models import User

from .serializers import (
   UserLoginSerializer,
   UserSerializer,
   UserSignupSerializer,
   ForgotPasswordSerializer,
   VerifyCodeSerializer,
   ResetPasswordSerializer,
   ListingSerializer
)
from django.shortcuts import render
from .serializers import USSDPUSHSerializer, PaymentSerializer
from .daraja import DarajaAPI
from rest_framework.decorators import api_view, APIView
from payment.models import Payment
from reviews.models import Review
from .serializers import ReviewSerializer
from django_filters.rest_framework import DjangoFilterBackend
import json
from django.core.cache import cache

class ReviewViewSet(viewsets.ModelViewSet):
   queryset = Review.objects.all()
   serializer_class = ReviewSerializer
  
  
otp_storage = {}

class UserViewSet(viewsets.ModelViewSet):

   queryset = User.objects.all()
   serializer_class = UserSerializer
   filter_backends = [DjangoFilterBackend]
   filterset_fields = ['role']
   http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']


class UserSignupAPIView(generics.CreateAPIView):
   queryset = User.objects.all()
   serializer_class = UserSignupSerializer
   permission_classes = [AllowAny]


class UserLocationViewSet(viewsets.ModelViewSet):
   queryset = UserLocation.objects.all()
   permission_classes = [AllowAny]

  
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
       cache.set(f'otp_{email}',otp,timeout=300)
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
       cached_otp=cache.get(f'otp_{email}')
       if cached_otp is None:
           return Response({"detail": "Otp has expired"},status=status.HTTP_400_BAD_REQUEST)
       cache.delete(f"otp_{email}")

    #    if otp_storage.get(email) != otp:
    #        return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


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
       cache.delete(f"otp_{email}")
    #    otp_storage.pop(email, None)
       return Response({"detail": "Password reset successful."})

class OrderViewSet(viewsets.ModelViewSet):
   queryset = Order.objects.all()
   serializer_class = OrderSerializer
   permission_classes = [AllowAny]

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

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
class USSDPUSHView(APIView):
    def post(self, request):
        serializer = USSDPUSHSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            daraja = DarajaAPI()
            try:
                ussd_response = daraja.ussd_push(
                    phone_number=data["phone_number"],
                    amount=float(data["amount"]),
                    account_reference=data["account_reference"],
                    transaction_desc=data["transaction_desc"],
                )
            except Exception as e:
                return Response(
                    {"error": f"Daraja API failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            merchant_request_id = ussd_response.get("MerchantRequestID")
            checkout_request_id = ussd_response.get("CheckoutRequestID")
            print("\n" + "="*70)
            print("DARAJA RESPONSE RECEIVED")
            print("="*70)
            print(f"MerchantRequestID: {merchant_request_id}")
            print(f"CheckoutRequestID: {checkout_request_id}")
            print("="*70 + "\n")
            if not checkout_request_id:
                return Response(
                    {"error": "Daraja did not return CheckoutRequestID"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            payment = Payment.objects.create(
                amount=float(data["amount"]),
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                status="pending",
            )
            return Response(
                {
                    "message": "USSD Push initiated, check your phone to complete the payment.",
                    "response": ussd_response,
                    "payment_id": payment.transaction_id,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(["POST"])
def mpesa_ussd_callback(request):
    print("\n" + "="*80)
    print("RECEIVED MPESA CALLBACK")
    print("="*80)
    print("Raw Request Data:", json.dumps(request.data, indent=2))
    print("="*80 + "\n")
    body = request.data.get("Body", {})
    stk_callback = body.get("stkCallback", {})
    merchant_request_id = stk_callback.get("MerchantRequestID")
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = int(stk_callback.get("ResultCode", 1))
    result_desc = stk_callback.get("ResultDesc")
    print(f"Searching Payment with:")
    print(f"  - CheckoutRequestID: '{checkout_request_id}'")
    print(f"  - MerchantRequestID: '{merchant_request_id}'")
    payment = None
    if checkout_request_id:
        try:
            payment = Payment.objects.get(checkout_request_id=checkout_request_id)
            print(f"Payment FOUND by CheckoutRequestID: ID={payment.transaction_id}")
        except Payment.DoesNotExist:
            print(f"Payment NOT FOUND by CheckoutRequestID: {checkout_request_id}")
    if not payment and merchant_request_id:
        try:
            payment = Payment.objects.get(merchant_request_id=merchant_request_id)
            print(f"Payment FOUND by MerchantRequestID: ID={payment.transaction_id}")
        except Payment.DoesNotExist:
            print(f"Payment NOT FOUND by MerchantRequestID: {merchant_request_id}")
    if not payment:
        print("NO PAYMENT FOUND WITH PROVIDED IDs")
        return Response({"error": "Payment not found"}, status=404)
    payment.merchant_request_id = merchant_request_id
    payment.result_code = str(result_code)
    payment.result_desc = result_desc
    receipt_url = None
    if result_code == 0:
        metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        parsed_metadata = {item["Name"]: item.get("Value") for item in metadata}
        payment.mpesa_receipt_number = parsed_metadata.get("MpesaReceiptNumber")
        payment.amount = parsed_metadata.get("Amount", payment.amount)
        payment.phone_number = parsed_metadata.get("PhoneNumber", "")
        txn_date = parsed_metadata.get("TransactionDate")
        if txn_date:
            try:
                txn_date_str = str(txn_date)
                payment.payment_date = datetime.strptime(txn_date_str, "%Y%m%d%H%M%S")
            except Exception as e:
                print(f"Failed to parse TransactionDate: {e}")
        payment.status = "confirmed"
    else:
        payment.status = "failed"
    payment.save()
    print(f"Payment {payment.transaction_id} UPDATED to status: {payment.status}")
    return Response({
        "ResultCode": 0,
        "ResultDesc": "Callback processed successfully",
        "receipt_url": receipt_url,
    })









