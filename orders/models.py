from django.db import models
from django.db.models import Sum, F
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('preparing', 'En préparation'),
        ('ready', 'Prêt'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]
    
    table_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Table {self.table_number} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_total(self):
        """Calcule le total de la commande en utilisant le related_name 'items'"""
        total = self.items.aggregate(          # ← Ici c'est 'items' et non 'orderitem_set'
            total=Sum(F('quantity') * F('price'))
        )['total']
        return float(total) if total else 0.0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def subtotal(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"