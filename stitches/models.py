from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Tops', 'Tops'),
        ('Skirts', 'Skirts'),
        ('Bags', 'Bags'),
        ('Scrunchies', 'Scrunchies'),
        ('Hair Bands', 'Hair Bands'),
        ('Bows', 'Bows'),
        ('Handkerchiefs', 'Handkerchiefs'),
        ('Others', 'Others'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Unisex')
    badge = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    def discount_percentage(self):
        if self.discount_price and self.price > self.discount_price:
            diff = self.price - self.discount_price
            percent = (diff / self.price) * 100
            return int(percent)
        return None


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Stitching', 'Stitching'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    state = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)

    # MEASUREMENTS
    chest = models.CharField(max_length=20, blank=True, null=True)
    waist = models.CharField(max_length=20, blank=True, null=True)
    hip = models.CharField(max_length=20, blank=True, null=True)
    shoulder = models.CharField(max_length=20, blank=True, null=True)
    sleeve = models.CharField(max_length=20, blank=True, null=True)
    top_length = models.CharField(max_length=20, blank=True, null=True)
    trouser_length = models.CharField(max_length=20, blank=True, null=True)
    thigh = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # FABRIC
    fabric = models.CharField(max_length=100, blank=True, null=True)
    colour = models.CharField(max_length=100, blank=True, null=True)

    # ORDER INFO
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} - {self.full_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    def subtotal(self):
        return self.price * self.quantity