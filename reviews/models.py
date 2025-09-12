from django.db import models
from user.models import User
from orders.models import Order


class Review(models.Model):
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} stars") for i in range(1, 6)] 
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('reviewer', 'order')  
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.id} by {self.reviewer.first_name} {self.reviewer.last_name} - {self.rating}★"