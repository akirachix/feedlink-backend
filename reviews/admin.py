from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'reviewer', 'order', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__first_name', 'reviewer__last_name', 'order__order_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']    
