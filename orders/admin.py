from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem

User = get_user_model()

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Configuration de l'interface admin pour le modèle User personnalisé
    """
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    pass

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'available', 'created_by', 'created_at')
    list_filter = ('available', 'category')
    search_fields = ('name',)
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'price', 'category', 'available')
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'table_number')
    search_fields = ('table_number',)
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de la commande', {
            'fields': ('table_number', 'status')
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    pass

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__table_number', 'product__name')
    pass

# Enregistrement des modèles dans l'admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
# admin.site.register(Product, ProductAdmin)
# admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem, OrderItemAdmin)