from django.db import models
from django.utils import timezone
from orders.models import Order
from user.models import User
PAYMENT_STATUS = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('failed', 'Failed'),
)
class Payment(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order,on_delete=models.CASCADE, verbose_name="Order", null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount (KES)")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    mpesa_receipt_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    result_code = models.CharField(max_length=10, blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True, verbose_name="Payment Date")
    status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS)
    status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS)
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} KES"
    def is_successful(self):
        return self.status == 'confirmed'
