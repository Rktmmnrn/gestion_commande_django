from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Order, OrderItem
from .serializers import CategorySerializer , ProductSerializer, OrderSerializer, OrderItemSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset= Category.objects.all()
    serializer_class= CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset= Product.objects.all()
    serializer_class= ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', 'category']

class OrderViewSet(viewsets.ModelViewSet):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table_number', 'status']
    
    def create(self, request, *args, **kwargs):
        # Extraire les items du body
        items_data = request.data.pop('items', [])
        
        # Passer les items au serializer via le context
        serializer = self.get_serializer(data=request.data, context={'items': items_data})
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
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='add_item')
    def add_item(self, request, pk=None):
        order = self.get_object()
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        
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
        
        serializer = OrderItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)