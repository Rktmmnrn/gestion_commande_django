from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('orders', views.OrderViewSet)
router.register('orderitems', views.OrderItemViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]