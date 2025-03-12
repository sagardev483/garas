from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="No description available")  # Default description
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    featured = models.BooleanField(default=False)  # For homepage featured section

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])

    def get_featured_products(self):
        """Returns featured products in this category."""
        return self.products.filter(featured=True)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="No description available")  # Default description
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)  # Option for featured products on homepage

    def __str__(self):
        return self.name

    def get_display_price(self):
        if self.is_sale and self.sale_price:
            return self.sale_price
        return self.price

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def in_stock(self):
        """Returns true if the product is in stock."""
        return self.stock > 0


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, default="")  # Default empty string
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_subtotal(self):
        return float(self.product.get_display_price()) * self.quantity

    def save(self, *args, **kwargs):
        """Override save to update the product stock when the cart item is created."""
        if self.product.stock >= self.quantity:
            super().save(*args, **kwargs)
        else:
            raise ValueError("Not enough stock available")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.pk}"

    def get_total_price(self):
        """Calculates the total price of the order based on order items."""
        return sum(item.quantity * item.price for item in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
