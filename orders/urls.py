from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer
from . import views

# Créer la vue personnalisée pour le token
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('orders', views.OrderViewSet)
router.register('orderitems', views.OrderItemViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]