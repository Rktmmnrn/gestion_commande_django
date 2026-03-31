from rest_framework import serializers
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

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'price', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.quantity * obj.price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'items', 'total', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total(self, obj):
        return obj.get_total()
    
    def validate(self, data):
        # Vérifier s'il existe une commande active pour cette table
        table_number = data.get('table_number')
        
        # Récupérer la commande existante (pour les mises à jour)
        instance = self.instance
        
        # Vérifier s'il existe une commande active pour cette table
        active_orders = Order.objects.filter(
            table_number=table_number,
            status__in=['pending', 'preparing', 'ready']
        )
        
        # Si c'est une mise à jour, exclure la commande actuelle
        if instance:
            active_orders = active_orders.exclude(id=instance.id)
        
        if active_orders.exists():
            raise serializers.ValidationError(
                f"La table {table_number} a déjà une commande en cours (statut: {active_orders.first().status})"
            )
        
        return data

    def create(self, validated_data):
        items_data = self.context.get('items', [])
        
        if not items_data:
            raise serializers.ValidationError("La commande doit au moins contenir un article")
        
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity', 1)
            
            if not product_id:
                order.delete()
                raise serializers.ValidationError("Chaque article doit avoir un ID de produit")
            
            try:
                product = Product.objects.get(id=product_id)
                if not product.available:
                    order.delete()
                    raise serializers.ValidationError(
                        f"Le produit '{product.name}' n'est pas disponible"
                    )
                if quantity <= 0:
                    order.delete()
                    raise serializers.ValidationError(
                        f"La quantité pour '{product.name}' doit être positive"
                    )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
            except Product.DoesNotExist:
                order.delete()
                raise serializers.ValidationError(f"Le produit avec l'ID {product_id} n'existe pas")
        
        return order