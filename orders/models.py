# Create your models here.
import secrets
from django.db import models
from django.utils import timezone
from inventory.models import Listing
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_pin(length=4):
    return ''.join(secrets.choice('0123456789') for _ in range(length))

class Order(models.Model):
    STATUS = [('pending', 'Pending'), ('picked', 'Picked')]
    PAYMENT_STATUS = [('paid', 'Paid'), ('unpaid', 'Unpaid')]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null= True)
    order_date = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=10, choices=STATUS, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='unpaid')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pin = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pin:
            pin = generate_pin()
            while Order.objects.filter(pin=pin).exists():
                pin = generate_pin()
            self.pin = pin
        super().save(*args, **kwargs)
        self.update_total_amount()

    def update_total_amount(self):
        total = self.items.aggregate(
            total=models.Sum(models.F('quantity') * models.F('price'), output_field=models.DecimalField())
        )['total'] or 0
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"Order {self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,  null= True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.listing and (self.price is None):
            self.price = self.listing.discounted_price
        super().save(*args, **kwargs)
        self.order.update_total_amount()

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order.order_id}"

class WasteClaim(models.Model):
    STATUS = [('pending', 'Pending'), ('collected', 'Collected')]
    waste_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims', null= True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name='claims', null= True)
    claim_time =  models.DateTimeField(null=True, blank=True) 
    claim_status = models.CharField(max_length=10, choices=STATUS, default='pending')
    pin = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.listing and self.listing.product_type != 'inedible':
            raise ValueError("Listing product_type must be 'inedible'")
        if not self.pin:
            pin = generate_pin()
            while WasteClaim.objects.filter(pin=pin).exists():
                pin = generate_pin()
            self.pin = pin
        super().save(*args, **kwargs)

    def __str__(self):
        return f"WasteClaim {self.waste_id}"
