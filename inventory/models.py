from django.db import models
from django.contrib.auth import get_user_model


class Listing(models.Model):
    
    PRODUCT_TYPE_CHOICES = [
        ('edible', 'Edible'),
        ('inedible', 'Inedible'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('expired', 'Expired'),
    ]
    UPLOAD_METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('csv', 'CSV'),
    ]

    listing_id = models.AutoField(primary_key=True) 
    producer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,limit_choices_to={'role':'producer'}, null=True) 
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateTimeField()
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upload_method = models.CharField(max_length=10, choices=UPLOAD_METHOD_CHOICES)
    pickup_window_duration = models.DateTimeField()

   
