from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Category, Product, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name', 'available']
        read_only_fields = ['id']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'product_price', 'quantity', 'price', 'subtotal']

    def get_subtotal(self, obj):
        return (obj.quantity or 0) * (obj.price or 0)
    
    def validate(self, data):
        """Valider les données du produit et de la commande"""
        order = data.get('order')
        product = data.get('product')
        quantity = data.get('quantity')
        
        # Vérifier que l'ordre existe
        if not order:
            raise serializers.ValidationError("Une commande est requise pour créer un article")
        
        # Vérifier que le produit existe
        if not product:
            raise serializers.ValidationError("Un produit est requis")
        
        # Vérifier que le produit est disponible
        if not product.available:
            raise serializers.ValidationError(
                f"Le produit '{product.name}' n'est pas disponible"
            )
        
        # Vérifier la quantité
        if quantity and quantity <= 0:
            raise serializers.ValidationError(
                "La quantité doit être positive"
            )
        
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'items', 'total', 
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total(self, obj):
        return obj.get_total()
    
    def validate(self, data):
        table_number = data.get('table_number')
        
        if not table_number:
            raise serializers.ValidationError("Le numéro de table est requis")
        
        return data

    def create(self, validated_data):
        items_data = self.context.get('items', [])
        request = self.context.get('request')
        table_number = validated_data.get('table_number')
        
        if not items_data:
            raise serializers.ValidationError("La commande doit au moins contenir un article")
        
        with transaction.atomic():
            # Vérifier s'il existe une commande pending pour cette table
            pending_order = Order.objects.filter(
                table_number=table_number,
                status='pending'
            ).first()
            
            if pending_order:
                # Réutiliser la commande existante
                order = pending_order
                print(f'📌 Réutilisation commande existante #{order.id} pour table {table_number}')
            else:
                order = Order.objects.create(**validated_data)
                print(f'✨ Nouvelle commande #{order.id} créée pour table {table_number}')
        
            # Ajouter les items à la commande (nouvelle ou existante)
            for item_data in items_data:
                product_id = item_data.get('product')
                quantity = item_data.get('quantity', 1)
                
                if not product_id:
                    raise serializers.ValidationError("Chaque article doit avoir un ID de produit")
                
                try:
                    product = Product.objects.get(id=product_id)
                    if not product.available:
                        raise serializers.ValidationError(
                            f"Le produit '{product.name}' n'est pas disponible"
                        )
                    if quantity <= 0:
                        raise serializers.ValidationError(
                            f"La quantité pour '{product.name}' doit être positive"
                        )
                    
                    # ✅ Vérifier si le produit existe déjà dans la commande
                    existing_item = OrderItem.objects.filter(
                        order=order, 
                        product=product
                    ).first()
                    
                    if existing_item:
                        # Augmenter la quantité
                        existing_item.quantity += quantity
                        existing_item.save()
                        print(f'➕ Quantité augmentée pour {product.name} ({existing_item.quantity})')
                    else:
                        # Créer un nouvel item
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )
                        print(f'🆕 Nouvel item: {product.name} x{quantity}')
                        
                except Product.DoesNotExist:
                    raise serializers.ValidationError(f"Le produit avec l'ID {product_id} n'existe pas")

            order.save()            
            return order

    def update(self, instance, validated_data):
        # Mettre à jour updated_by
        request = self.context.get('request')
        instance.save()

        return super().update(instance, validated_data)