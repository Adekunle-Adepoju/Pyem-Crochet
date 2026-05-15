from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'gender']
    list_filter = ['category', 'gender']
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'state', 'total', 'status', 'created_at']
    list_filter = ['status', 'state']
    search_fields = ['full_name', 'email', 'phone']
    list_editable = ['status']
    inlines = [OrderItemInline]