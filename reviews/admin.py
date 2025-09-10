from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # list_display = ['review_id', 'user_id', 'order_id', 'ratings']
    # search_fields = ['user_id', 'order_id']
    list_filter = ['ratings']