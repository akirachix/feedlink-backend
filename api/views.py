from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token

import random
from location.models import UserLocation
from user.models import User
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
   
    ForgotPasswordSerializer,
    VerifyCodeSerializer,
    ResetPasswordSerializer,
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
    


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
     'users': reverse('user-list', request=request, format=format),
     'signup': reverse('user-signup', request=request, format=format),
     'login': reverse('user-login', request=request, format=format),
    })


