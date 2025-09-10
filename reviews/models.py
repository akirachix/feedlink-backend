from django.db import models
# from user.models import User
# from order.models import Order

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    # user_id = models.ForeignKey(
    #     User,
    #     to_field='user_id',
    #     on_delete=models.CASCADE,
    #     related_name="reviews"
    #     )
    # order_id = models.ForeignKey(
    #     Order,
    #     to_field='order_id',
    #     on_delete=models.CASCADE,
    #     related_name="reviews"
    # )
    ratings = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'reviews'
        # unique_together = ('user_id', 'order_id')

    def __str__(self):
        return f"Review {self.review_id} - {self.ratings} stars"
