from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Category, Product, Order, OrderItem

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personnalisation du serializer JWT pour ajouter username, role, is_staff, is_superuser
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Ajouter les données utilisateur dans le token
        token['user_id'] = user.id
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        
        # Ajouter le rôle si c'est un utilisateur personnalisé
        if hasattr(user, 'role'):
            token['role'] = user.role
        
        return token

class UserMinimalSerializer(serializers.ModelSerializer):
    """Sérialiseur minimal pour afficher created_by/updated_by"""
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour la gestion des utilisateurs"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['date_joined', 'last_login']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        # Mettre à jour les champs
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    created_by_info = UserMinimalSerializer(source='created_by', read_only=True)
    updated_by_info = UserMinimalSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name', 'available',
                  'created_by', 'created_by_info', 'updated_by', 'updated_by_info',
                  'created_at', 'updated_at']
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']

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
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    total = serializers.SerializerMethodField()
    created_by_info = UserMinimalSerializer(source='created_by', read_only=True)
    updated_by_info = UserMinimalSerializer(source='updated_by', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'items', 'total', 
                  'created_at', 'updated_at',
                  'created_by', 'created_by_info', 'updated_by', 'updated_by_info']
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    def get_total(self, obj):
        return obj.get_total()
    
    def validate(self, data):
        # Validation basique - la logique de commande existante est dans create()
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
            # 🔍 OPTION B: Vérifier s'il existe une commande pending pour cette table
            pending_order = Order.objects.filter(
                table_number=table_number,
                status='pending'
            ).first()
            
            if pending_order:
                # Réutiliser la commande existante
                order = pending_order
                print(f'📌 Réutilisation commande existante #{order.id} pour table {table_number}')
            else:
                # Créer une nouvelle commande
                validated_data['created_by'] = request.user if request else None
                validated_data['updated_by'] = request.user if request else None
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
            
            # Mettre à jour le timestamp de la commande
            order.updated_by = request.user if request else None
            order.save()
            
            return order

    def update(self, instance, validated_data):
        # Mettre à jour updated_by
        request = self.context.get('request')
        instance.updated_by = request.user if request else None
        instance.save()

        return super().update(instance, validated_data)