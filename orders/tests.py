from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Category, Product, Order, OrderItem

User = get_user_model()


class UserModelTest(TestCase):
    """Tests pour le modèle User personnalisé"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.waiter_user = User.objects.create_user(
            username='waiter',
            password='waiter123',
            role='waiter'
        )
    
    def test_admin_user_is_staff(self):
        """Vérifier que l'admin a is_staff=True"""
        self.assertTrue(self.admin_user.is_staff)
    
    def test_waiter_user_is_not_staff(self):
        """Vérifier que le serveur a is_staff=False"""
        self.assertFalse(self.waiter_user.is_staff)
    
    def test_user_creation_with_role(self):
        """Vérifier la création d'un utilisateur avec un rôle"""
        self.assertEqual(self.admin_user.role, 'admin')
        self.assertEqual(self.waiter_user.role, 'waiter')


class JWTAuthenticationTest(TestCase):
    """Tests pour l'authentification JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='waiter'
        )
        self.token_url = '/api/token/'
        self.refresh_url = '/api/token/refresh/'
    
    def test_obtain_token(self):
        """Tester l'obtention d'un token JWT"""
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_obtain_token_invalid_credentials(self):
        """Tester l'obtention d'un token avec des identifiants invalides"""
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token(self):
        """Tester le rafraîchissement du token"""
        # Obtenir un token
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = response.data['refresh']
        
        # Rafraîchir le token
        response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class PermissionTest(TestCase):
    """Tests pour les permissions"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.waiter_user = User.objects.create_user(
            username='waiter',
            password='waiter123',
            role='waiter'
        )
        self.category = Category.objects.create(name='Test Category')
    
    def test_admin_can_create_product(self):
        """Vérifier que l'admin peut créer un produit"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'price': '10.00',
            'category': self.category.id,
            'available': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_waiter_cannot_create_product(self):
        """Vérifier que le serveur ne peut pas créer un produit"""
        self.client.force_authenticate(user=self.waiter_user)
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'price': '10.00',
            'category': self.category.id,
            'available': True
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_waiter_can_read_product(self):
        """Vérifier que le serveur peut lire les produits"""
        self.client.force_authenticate(user=self.waiter_user)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_can_delete_product(self):
        """Vérifier que l'admin peut supprimer un produit"""
        product = Product.objects.create(
            name='Test Product',
            price='10.00',
            category=self.category,
            available=True
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AuditFieldsTest(TestCase):
    """Tests pour les champs d'audit (created_by, updated_by)"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.admin_user)
    
    def test_product_created_by_auto_set(self):
        """Vérifier que created_by est automatiquement défini lors de la création"""
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'price': '10.00',
            'category': self.category.id,
            'available': True
        })
        product = Product.objects.get(id=response.data['id'])
        self.assertEqual(product.created_by, self.admin_user)
    
    def test_product_updated_by_auto_set(self):
        """Vérifier que updated_by est automatiquement défini lors de la mise à jour"""
        product = Product.objects.create(
            name='Test Product',
            price='10.00',
            category=self.category,
            available=True,
            created_by=self.admin_user
        )
        
        response = self.client.put(f'/api/products/{product.id}/', {
            'name': 'Updated Product',
            'price': '15.00',
            'category': self.category.id,
            'available': True
        })
        
        product.refresh_from_db()
        self.assertEqual(product.updated_by, self.admin_user)
    
    def test_order_created_by_auto_set(self):
        """Vérifier que created_by est automatiquement défini lors de la création d'une commande"""
        product = Product.objects.create(
            name='Test Product',
            price='10.00',
            category=self.category,
            available=True,
            created_by=self.admin_user
        )
        
        response = self.client.post('/api/orders/', {
            'table_number': 1,
            'status': 'pending',
            'items': [
                {'product': product.id, 'quantity': 2}
            ]
        }, format='json')
        
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.created_by, self.admin_user)


class UserCRUDTest(TestCase):
    """Tests pour les opérations CRUD sur les utilisateurs"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.waiter_user = User.objects.create_user(
            username='waiter',
            password='waiter123',
            role='waiter'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_admin_can_list_users(self):
        """Vérifier que l'admin peut lister tous les utilisateurs"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin et waiter
    
    def test_admin_can_create_user(self):
        """Vérifier que l'admin peut créer un utilisateur"""
        response = self.client.post('/api/users/', {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com',
            'role': 'waiter'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
    
    def test_admin_can_delete_user(self):
        """Vérifier que l'admin peut supprimer un utilisateur"""
        response = self.client.delete(f'/api/users/{self.waiter_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
    
    def test_waiter_cannot_list_users(self):
        """Vérifier que le serveur ne peut pas lister tous les utilisateurs"""
        self.client.force_authenticate(user=self.waiter_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_waiter_can_read_own_profile(self):
        """Vérifier que le serveur peut lire son propre profil"""
        self.client.force_authenticate(user=self.waiter_user)
        response = self.client.get(f'/api/users/{self.waiter_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'waiter')
    
    def test_waiter_can_update_own_profile(self):
        """Vérifier que le serveur peut mettre à jour son propre profil"""
        self.client.force_authenticate(user=self.waiter_user)
        response = self.client.patch(f'/api/users/{self.waiter_user.id}/', {
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.waiter_user.refresh_from_db()
        self.assertEqual(self.waiter_user.email, 'updated@example.com')