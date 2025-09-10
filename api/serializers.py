from rest_framework import serializers
from user.models import User

from django.contrib.auth import get_user_model, authenticate
from location.models import UserLocation
from location.utils import geocode_address


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        User = get_user_model()
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        attrs['user'] = user
        return attrs





class UserSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email',
            'role', 'profile_picture', 'address',
            'till_number', 'latitude', 'longitude'
        ]

   

    def get_latitude(self, obj):
        location = UserLocation.objects.filter(user=obj).first()
        return location.latitude if location else None
    def get_longitude(self, obj):
         location = UserLocation.objects.filter(user=obj).first()
         return location.longitude if location else None

    def create(self, validated_data):
        address = validated_data.get('address')
        till_number = validated_data.get('till_number')
        role = validated_data.get('role')

        if role != 'producer':
            if address:
                raise serializers.ValidationError(
                    {"address": "Only producers can provide an address."}
                )
            if till_number:
                raise serializers.ValidationError(
                    {"till_number": "Only producers can provide a till number."}
                )

        user = User.objects.create(**validated_data)

        if role == 'producer' and address:
            lat, lon = geocode_address(address)
            UserLocation.objects.create(
                user=user,
                address=address,
                latitude=lat,
                longitude=lon
            )
        return user

    def update(self, instance, validated_data):
        address = validated_data.get('address', instance.address)
        till_number = validated_data.get('till_number', instance.till_number)
        role = validated_data.get('role', instance.role)

        if role != 'producer':
            if 'address' in validated_data and validated_data['address']:
                raise serializers.ValidationError(
                    {"address": "Only producers can update an address."}
                )
            if 'till_number' in validated_data and validated_data['till_number']:
                raise serializers.ValidationError(
                    {"till_number": "Only producers can update a till number."}
                )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if role == 'producer' and address:
            lat, lon = geocode_address(address)
            location_qs = UserLocation.objects.filter(user=instance)
            if location_qs.exists():
                location = location_qs.first()
                location.address = address
                location.latitude = lat
                location.longitude = lon
                location.save()
            else:
                UserLocation.objects.create(
                    user=instance,
                    address=address,
                    latitude=lat,
                    longitude=lon
                )
        return instance

class UserSignupSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "email",
            "password", "role", "till_number",
            "profile_picture", "address",
            "latitude", "longitude"
        ]
        extra_kwargs = {
            "password": {"write_only": True}  
        }
  
  
    def get_latitude(self, obj):
          location = UserLocation.objects.filter(user=obj).first()
          return location.latitude if location else None
    def get_longitude(self, obj):
           location = UserLocation.objects.filter(user=obj).first()
           return location.longitude if location else None
    






    def create(self, validated_data):
        role = validated_data.get("role")
        address = validated_data.get("address")
        till_number = validated_data.get("till_number")
    
        if role != "producer":
            if address:
                raise serializers.ValidationError(
                    {"address": "Only producers can provide an address."}
                )
            if till_number:
                raise serializers.ValidationError(
                    {"till_number": "Only producers can provide a till number."}
                )
     
        user = User.objects.create_user(
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            till_number=till_number if role == "producer" else None,
            profile_picture=validated_data.get("profile_picture", ""),
            address=address if role == "producer" else None,
        )
      
        if role == "producer" and address:
            latitude, longitude = geocode_address(address)
            UserLocation.objects.create(
                user=user,
                address=address,
                latitude=latitude,
                longitude=longitude,
            )
        return user


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = "__all__"

    def create(self, validated_data):
        address = validated_data.get("address", "")
        if address:
            lat, lon = geocode_address(address)
            validated_data["latitude"] = lat
            validated_data["longitude"] = lon
        return super().create(validated_data)

    def update(self, instance, validated_data):
        address = validated_data.get("address", instance.address)
        if address and address != instance.address:
            lat, lon = geocode_address(address)
            validated_data["latitude"] = lat
            validated_data["longitude"] = lon
        return super().update(instance, validated_data)
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Password does not match.")
        return attrs
