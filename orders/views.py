from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Order, OrderItem, Client, Table, Reservation
from .serializers import CategorySerializer , ProductSerializer, OrderSerializer, OrderItemSerializer, ClientSerializer, TableSerializer, ReservationSerializer
from .permissions import IsAdminOrReadOnly, IsAdminPasswordVerified, IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny


class CategoryViewSet(viewsets.ModelViewSet):
    queryset= Category.objects.all()
    serializer_class= CategorySerializer
    permission_classes= [IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset= Product.objects.all()
    serializer_class= ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', 'category']
    permission_classes = [IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table', 'status']
    permission_classes = [AllowAny]
    
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

        if order.table:
            if new_status == 'delivered':
                order.table.status = 'libre'
            else:
                order.table.status = 'occupee'

            order.table.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminOrReadOnly]


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [AllowAny]


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        reservation = serializer.save()

        confirmation_url = (
            f"http://localhost:8000/api/reservations/confirm/"
            f"{reservation.token_confirmation}/"
        )

        if reservation.client and reservation.client.email:
            send_mail(
                subject="Confirmation de réservation",
                message=(
                    f"Bonjour {reservation.client.nom},\n\n"
                    f"Confirmez votre réservation ici :\n"
                    f"{confirmation_url}"
                ),
                from_email=None,
                recipient_list=[reservation.client.email],
                fail_silently=True
            )


@api_view(['GET'])
@permission_classes((AllowAny,))
def confirm_reservation(request, token):
    reservation = get_object_or_404(
        Reservation,
        token_confirmation=token
    )
    reservation.confirm_client = True
    reservation.save()
    return HttpResponse(
        "<h1>Réservation confirmée avec succès</h1>"
    )