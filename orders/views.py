from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Order, OrderItem
from .serializers import CategorySerializer , ProductSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsAdminOrReadOnly, IsAdminPasswordVerified, IsAuthenticatedOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset= Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes= [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset= Product.objects.all()
    serializer_class= ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', 'category']
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table_number', 'status']
    permission_classes = [IsAdminOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        items_data = request.data.get('items', [])
        serializer = self.get_serializer(data=request.data, context={
            'items': items_data,
            'request': request
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminOrReadOnly]