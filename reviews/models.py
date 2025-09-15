from django.db import models
from user.models import User
from orders.models import Order
from django.contrib.auth import get_user_model



class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,limit_choices_to={'role':'buyer'})  
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    ratings = models.PositiveSmallIntegerField() 


    class Meta:
        unique_together = ('user', 'order')  

    def __str__(self):
        return f"Review {self.pk} by {self.user} for Order {self.order}"