from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
   

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  
    first_name = models.CharField(max_length=20, blank=False, null=False)
    last_name = models.CharField(max_length=20, blank=False, null=False)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/',blank=True, null=True)
    ROLE = [
        ('recycler', 'Recycler'),
        ('buyer', 'Buyer'),
        ('producer', 'Producer'),
        ('admin','Admin')
    ]
    role = models.CharField(max_length=10, choices=ROLE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    till_number = models.CharField(max_length=6, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = []  

    objects = CustomUserManager()

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email