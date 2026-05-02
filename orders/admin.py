from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Category, Product, Order, OrderItem

# Réenregistrer le User (modèle Django standard) avec une vue plus propre
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_superuser', 'is_active', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'available')
    list_filter = ('available', 'category')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'status', 'created_at', 'get_total_display')
    list_filter = ('status', 'table_number')
    search_fields = ('table_number',)
    readonly_fields = ('created_at', 'updated_at')

    def get_total_display(self, obj):
        return f"{obj.get_total():.2f} Ar"
    get_total_display.short_description = 'Total'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'subtotal_display')
    list_filter = ('order__table_number', 'order__status')
    search_fields = ('product__name',)
    readonly_fields = ('price', 'subtotal_display')

    def subtotal_display(self, obj):
        if obj.price and obj.quantity:
            return f"{obj.subtotal():.2f} Ar"
        return "-"
    
    subtotal_display.short_description = 'Sous-total'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Rendre le champ price en lecture seule dans le formulaire
        if 'price' in form.base_fields:
            form.base_fields['price'].disabled = True
        return form