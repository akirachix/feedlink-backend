from django.db import models

# Create your models here.
import secrets
from django.db import models
from django.utils import timezone
# from django.contrib.auth import get_user_model

# User = get_user_model()

def generate_pin(length=4):
    return ''.join(secrets.choice('0123456789') for _ in range(length))

class Order(models.Model):
    STATUS = [('pending', 'Pending'), ('picked', 'Picked')]
    PAYMENT_STATUS = [('paid', 'Paid'), ('unpaid', 'Unpaid')]

    order_id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # listing = models.ForeignKey(Inventory, on_delete=models.CASCADE)
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

    def __str__(self):
        return f"Order {self.order_id} "

class WasteClaim(models.Model):
    STATUS = [('pending', 'Pending'), ('collected', 'Collected')]
    waste_id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waste_claims')
    # listing = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    claim_time =  models.DateTimeField(null=True, blank=True) 
    claim_status = models.CharField(max_length=10, choices=STATUS, default='pending')
    pickup_window_end = models.DateTimeField()
    pin = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pin:
            pin = generate_pin()
            while WasteClaim.objects.filter(pin=pin).exists():
                pin = generate_pin()
            self.pin = pin
        super().save(*args, **kwargs)

    def __str__(self):
        return f"WasteClaim {self.waste_id}"
