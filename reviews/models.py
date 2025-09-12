from django.db import models
from user.models import User
from orders.models import Order


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    ratings = models.PositiveSmallIntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'order')  

    def __str__(self):
        return f"Review {self.review_id} by {self.user.email} for Order {self.order.order_id}"