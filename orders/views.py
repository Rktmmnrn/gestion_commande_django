from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem
from .serializers import CategorySerializer , ProductSerializer, OrderSerializer, OrderItemSerializer, UserSerializer
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrAdmin
from rest_framework.permissions import AllowAny

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs.
    Admins: CRUD complet
    Waiters: Lecture seule sur leur propre profil
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        Permissions personnalisées selon l'action
        """
        if self.action in ['list', 'create', 'destroy']:
            # Seuls les admins peuvent lister, créer ou supprimer
            self.permission_classes = [IsAdmin]
        elif self.action in ['update', 'partial_update']:
            # Admins ou propriétaire pour la modification
            self.permission_classes = [IsOwnerOrAdmin]
        else:
            # Lecture: authentifié requis
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Les serveurs ne voient que leur propre profil
        """
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset= Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset= Product.objects.all()
    serializer_class= ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', 'category']
    permission_classes = [AllowAny]
    # permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        """Auto-set created_by lors de la création"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Auto-set updated_by lors de la mise à jour"""
        serializer.save(updated_by=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table_number', 'status']
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Permissions personnalisées selon l'action
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            # Seuls les admins peuvent modifier/supprimer les commandes existantes
            self.permission_classes = [IsAdmin]
        else:
            # Les serveurs peuvent créer et lire
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        # Extraire les items du body
        items_data = request.data.get('items', [])
        
        # Passer les items au serializer via le context
        serializer = self.get_serializer(data=request.data, context={
            'items': items_data,
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        # Vérifier que le statut est valide
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour uniquement le statut
        order.status = new_status
        order.updated_by = request.user
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='add_item')
    def add_item(self, request, pk=None):
        order = self.get_object()
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        # validation des quantités
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response (
                    {'error': 'Quantity must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response (
                {'error': 'Quantity must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le produit existe
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with id {product_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier que le produit est disponible
        if not product.available:
            return Response(
                {'error': f'Product {product.name} is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'item existe déjà dans la commande
        existing_item = OrderItem.objects.filter(order=order, product=product).first()
        
        if existing_item:
            # Mettre à jour la quantité si l'item existe déjà
            existing_item.quantity += quantity
            existing_item.save()
            item = existing_item
        else:
            # Créer un nouvel item
            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
        
        # Mettre à jour le champ updated_by de la commande
        order.updated_by = request.user
        order.save()

        serializer = OrderItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]