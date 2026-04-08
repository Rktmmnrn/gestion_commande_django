from django.db import models
from django.db.models import Sum, F
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('waiter', 'Serveur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='waiter')

    class Meta:
        ordering = ['username']
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def save(self, *args, **kwargs):
        # Synchroniser is_staff avec le rôle admin
        if self.role == 'admin':
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

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
    # audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='products_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='products_updated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
     # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='orders_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders_updated'
    )

    class Meta:
        ordering = ['-created_at'] # les plus récents d'abord
    
    def __str__(self):
        return f"Table {self.table_number} - {self.created_at}"
    
    def get_total(self):
        """Calcule le total de la commande en utilisant une requête optimisée"""
        total = self.orderitem_set.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total']
        return float(total) if total else 0.0

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    