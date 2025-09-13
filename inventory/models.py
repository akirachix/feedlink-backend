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
    UNIT_CHOICES = [
    ('kg', 'kg'),
    ('L', 'L'),
    ('unit', 'unit'), 
]
    listing_id = models.AutoField(primary_key=True) 
    producer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,limit_choices_to={'role':'producer'})  
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES)
    category = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upload_method = models.CharField(max_length=10, choices=UPLOAD_METHOD_CHOICES)
    pickup_window_duration = models.DateTimeField()
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        help_text="Select the unit: kg (weight), L (volume), or unit (count of items)"
    )
    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.product_type}"

   
