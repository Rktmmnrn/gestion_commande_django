import uuid
from django.db import models
from django.db.models import Sum, F
from django.conf import settings


class Client(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=30)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nom


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
    

class Table(models.Model):
    STATUS_CHOICES = [
        ('free', 'Libre'),
        ('occuped', 'Occupee'),
    ]

    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='free'
    )

    def __str__(self):
        return f"Table {self.number}"


class Reservation(models.Model):
    STATUT_CHOICES = [
        ('waiting', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('canceled', 'Annulée'),
    ]
    TYPE_COMMANDE_CHOICES = [
        ('on_site', 'Sur place'),
        ('online', 'En ligne'),
        ('take_away', 'À emporter'),
    ]
    date_heure = models.DateTimeField()
    nb_personnes = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='waiting')
    type_commande = models.CharField(max_length=20, choices=TYPE_COMMANDE_CHOICES, default='on_site')
    confirm_client = models.BooleanField(default=False)
    token_confirmation = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')

    def __str__(self):
        return f"Réservation #{self.id}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('preparing', 'En préparation'),
        ('ready', 'Prêt'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]
    TYPE_COMMANDE_CHOICES = [
        ('on_site', 'Sur place'),
        ('online', 'En ligne'),
        ('take_away', 'À emporter'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True,related_name='orders')
    type_commande = models.CharField(max_length=20, choices=TYPE_COMMANDE_CHOICES, default='on_site')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        table_num = self.table.number if self.table else "N/A"
        return f"Table {table_num} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_total(self):
        """Calcule le total de la commande en utilisant le related_name 'items'"""
        total = self.items.aggregate(
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
