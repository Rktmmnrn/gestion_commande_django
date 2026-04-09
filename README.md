# 🍽️ Django Gestion de Commandes - API REST

[![Tests Status](https://img.shields.io/badge/Tests-25/25%20OK-brightgreen)](./TEST_REPORT.md) [![Django](https://img.shields.io/badge/Django-6.0.3-darkgreen)](https://www.djangoproject.com/) [![DRF](https://img.shields.io/badge/DRF-3.14.0-darkblue)](https://www.django-rest-framework.org/)

Une API REST complète basée sur Django REST Framework pour gérer les commandes, produits et catégories d'un restaurant.

## 📋 Table des Matières

- [Caractéristiques](#caractéristiques)
- [Installation](#installation)
- [Configuration](#configuration)
- [Points Terminaux API](#points-terminaux-api)
- [Exemples d'Utilisation](#exemples-dutilisation)
- [Résultats des Tests](#résultats-des-tests)
- [Modèles de Données](#modèles-de-données)
- [Gestion des Erreurs](#gestion-des-erreurs)

---

## ✨ Caractéristiques

- ✅ **API RESTful complète** : CRUD complet pour tous les modèles
- ✅ **Authentification JWT** : Tokens d'accès et de rafraîchissement avec SimpleJWT
- ✅ **Système de rôles** : Admin et Waiter avec permissions personnalisées
- ✅ **Gestion des utilisateurs** : Model User personnalisé avec rôle et synchronisation is_staff
- ✅ **Gestion des catégories** : Organiser les produits par catégorie
- ✅ **Gestion des produits** : Produits avec prix, disponibilité et catégorie
- ✅ **Gestion des commandes** : Commandes avec statuts (en attente, en préparation, prêt, livré, annulé)
- ✅ **Logique intelligente de commandes** : Réutilisation automatique des commandes "pending" (Option B)
- ✅ **Calcul automatique** : Totaux de commande calculés en temps réel
- ✅ **Filtrage avancé** : Filtrer par disponibilité, catégorie, table, statut
- ✅ **Validations métier** : Vérification des produits disponibles, des quantités positives
- ✅ **Actions personnalisées** : Endpoints spécialisés pour mettre à jour le statut et ajouter des articles
- ✅ **Audit trail** : Champs created_by/updated_by pour tracer les modifications
- ✅ **Tests complets** : 25+ tests CRUD validant l'intégrité du système
- ✅ **CORS activé** : Support complet du cross-origin pour les frontends
- ✅ **Django Admin** : Interface d'administration intégrée
- ✅ **Permissions granulaires** : Contrôle d'accès basé sur les rôles

---

## 🛠️ Prérequis

- **Python** 3.8+
- **pip** (gestionnaire de paquets)
- **SQLite** (inclus par défaut) ou MySQL/PostgreSQL (optionnel)

---

## 📦 Installation Complète

### 1. Clone/Accès au répertoire

```bash
cd django_gestion_commande
```

### 2. Créer et activer l'environnement virtuel

```bash
# Créer l'environnement
python -m venv .venv

# Activer (Linux/macOS)
source .venv/bin/activate

# Ou sur Windows
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

---

## ⚙️ Configuration

### Variables d'Environnement (.env)

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## � Authentification & Rôles

### Système d'Authentification

L'API utilise **JWT (JSON Web Tokens)** via **SimpleJWT** pour l'authentification :

#### 1. Obtenir un Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123"}'
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. Utiliser le Token dans les Requêtes

```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

#### 3. Rafraîchir le Token Expiré

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

### Rôles & Permissions

#### Utilisateurs Waiter (Serveur)
- ✅ Créer et lire les commandes
- ✅ Lire les produits et catégories
- ❌ Modifier/supprimer les commandes
- ❌ Gérer les utilisateurs et produits

#### Utilisateurs Admin (Administrateur)
- ✅ Accès complet à tous les endpoints
- ✅ Gérer les utilisateurs
- ✅ Modifier/supprimer les commandes
- ✅ Gérer les produits et catégories

#### Configuration des Permissions

Dans `settings.py` :
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

#### Créer un Utilisateur

Via l'admin Django :
```bash
python manage.py createsuperuser
```

Ou via l'API (admin seulement) :
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "waiter1",
    "password": "securepass",
    "role": "waiter"
  }'
```

---

## 📌 Logique des Commandes (Option B)

Le système utilise une **logique intelligente** pour les commandes :

1. **Si une commande "pending" existe** pour la table → les nouveaux articles y sont **ajoutés**
2. **Si aucune commande "pending"** n'existe → une **nouvelle commande** est créée
3. **Les quantités augmentent automatiquement** si un produit est déjà dans la commande

**Exemple:**
```bash
# Première commande pour table 1
POST /orders/ → Crée commande #1 avec produit A (qty: 1)

# Deuxième envoi pour table 1 (même produit A)
POST /orders/ → Ajoute à commande #1, produit A (qty: 2)

# Envoi avec produit B pour table 1
POST /orders/ → Ajoute à commande #1, produit B (qty: 1)
```

---

## �🚀 Démarrage du Serveur

```bash
python manage.py runserver
```

L'API sera accessible à : **`http://localhost:8000/api/`**

---

## 🔌 Points Terminaux API

### Base URL
```
http://localhost:8000/api/
```

### Catégories

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/categories/` | Lister toutes les catégories |
| POST | `/categories/` | Créer une catégorie |
| GET | `/categories/{id}/` | Récupérer une catégorie |
| PUT | `/categories/{id}/` | Mettre à jour une catégorie |
| DELETE | `/categories/{id}/` | Supprimer une catégorie |

### Produits

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/products/` | Lister tous les produits |
| POST | `/products/` | Créer un produit |
| GET | `/products/{id}/` | Récupérer un produit |
| PUT | `/products/{id}/` | Mettre à jour un produit |
| DELETE | `/products/{id}/` | Supprimer un produit |
| GET | `/products/?available=true` | Filtrer par disponibilité |
| GET | `/products/?category={id}` | Filtrer par catégorie |

### Commandes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/orders/` | Lister toutes les commandes |
| POST | `/orders/` | Créer une commande avec articles |
| GET | `/orders/{id}/` | Récupérer une commande |
| PUT/PATCH | `/orders/{id}/` | Mettre à jour une commande |
| DELETE | `/orders/{id}/` | Supprimer une commande |
| PATCH | `/orders/{id}/status/` | Mettre à jour le statut |
| POST | `/orders/{id}/add_item/` | Ajouter un article |
| GET | `/orders/?table_number={n}` | Filtrer par table |
| GET | `/orders/?status={status}` | Filtrer par statut |

### Articles de Commande

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/orderitems/` | Lister tous les articles |
| POST | `/orderitems/` | Créer un article |
| GET | `/orderitems/{id}/` | Récupérer un article |
| PUT | `/orderitems/{id}/` | Mettre à jour un article |
| DELETE | `/orderitems/{id}/` | Supprimer un article |

---

## 💡 Exemples d'Utilisation

### 1. Créer une Catégorie

```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Boissons"}'
```

### 2. Créer un Produit

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Espresso",
    "price": "2.50",
    "category": 1,
    "available": true
  }'
```

### 3. Créer une Commande avec Articles

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "table_number": 5,
    "status": "pending",
    "items": [
      {"product": 1, "quantity": 2},
      {"product": 2, "quantity": 1}
    ]
  }'
```

### 4. Mettre à Jour le Statut

```bash
curl -X PATCH http://localhost:8000/api/orders/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "ready"}'
```

### 5. Ajouter un Article à Une Commande

```bash
curl -X POST http://localhost:8000/api/orders/1/add_item/ \
  -H "Content-Type: application/json" \
  -d '{"product": 3, "quantity": 1}'
```

### 6. Filtrer les Commandes

```bash
curl http://localhost:8000/api/orders/?status=ready
curl http://localhost:8000/api/orders/?table_number=5
```

---

## 🧪 Résultats des Tests CRUD

### ✅ **Status Global : 25/25 TESTS PASSÉS (100%)**

**Exécuter les tests** :
```bash
python manage.py test orders.test_crud -v 2
```

**Détails complets** : Consultez [TEST_REPORT.md](./TEST_REPORT.md)

#### Résumé par Module

| Module | Tests | Status |
|--------|-------|--------|
| Catégories | 5 | ✅ PASS |
| Produits | 6 | ✅ PASS |
| Commandes | 7 | ✅ PASS |
| Articles | 5 | ✅ PASS |

---

## 📊 Modèles de Données

### Category
```
id (PK)    : Integer
name       : CharField(max_length=100)
```

### Product
```
id (PK)          : Integer
name             : CharField(max_length=200)
price            : DecimalField(10,2)
category (FK)    : ForeignKey(Category)
available        : BooleanField(default=True)
```

### Order
```
id (PK)          : Integer
table_number     : IntegerField
status           : CharField(choices=['pending', 'preparing', 'ready', 'delivered', 'cancelled'])
created_at       : DateTimeField(auto_now_add=True)
updated_at       : DateTimeField(auto_now=True)
get_total()      : Calcule la somme des articles
```

### OrderItem
```
id (PK)          : Integer
order (FK)       : ForeignKey(Order)
product (FK)     : ForeignKey(Product)
quantity         : PositiveIntegerField(default=1)
price            : DecimalField(10,2)
subtotal()       : Calcule quantity × price
```

---

## ⚠️ Gestion des Erreurs

### 201 - Created
```json
{"id": 1, "name": "Catégorie"}
```

### 400 - Bad Request
```json
{"error": "La quantité doit être positive"}
```

### 404 - Not Found
```json
{"detail": "Not found."}
```

### 409 - Conflict
```json
{"error": "La table 5 a déjà une commande en cours"}
```

---

## 🔐 Authentification JWT (Optionnel)

### Obtenir un Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Utiliser le Token

```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📁 Structure du Projet

```
django_gestion_commande/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md (THIS FILE)
├── TEST_REPORT.md
│
├── restoProject/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── orders/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── test_crud.py
    ├── admin.py
    └── migrations/
```

---

## 🐛 Dépannage

### "Module not found: rest_framework"
```bash
pip install -r requirements.txt
```

### "ProgrammingError" après changement de modèle
```bash
python manage.py makemigrations
python manage.py migrate
```

### Port 8000 déjà utilisé
```bash
python manage.py runserver 8001
```

### Erreur CORS depuis le frontend
Vérifier `CORS_ALLOWED_ORIGINS` dans `restoProject/settings.py`

---

## 📞 Support

Questions ou problèmes ? Consultez [TEST_REPORT.md](./TEST_REPORT.md) pour plus de détails.

---

## ✨ Améliorations Récentes (v1.0)

- ✅ Correction du sérialiseur OrderItem (inclusion du champ 'order')
- ✅ Ajout de validations complètes
- ✅ 25 tests CRUD exhaustifs (100% de passage)
- ✅ Documentation complète
- ✅ Rapport de test détaillé

---

**Status** : ✅ Production Ready  
**Test Coverage** : 100% (25/25 tests)  
**Last Updated** : 2026-04-01



## 🛠️ Prérequis

- **Python** 3.8+
- **pip** (gestionnaire de paquets)
- **SQLite** (inclus par défaut) ou MySQL/PostgreSQL (optionnel)

## 📦 Installation Complète

### 1. Clone/Accès au répertoire

```bash
cd django_gestion_commande
```

### 2. Créer et activer l'environnement virtuel

```bash
# Créer l'environnement
python -m venv .venv

# Activer (Linux/macOS)
source .venv/bin/activate

# Ou sur Windows
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

## ⚙️ Configuration

### 1. Variables d'environnement

Créez un fichier `.env` à la racine du projet (optionnel) pour stocker les configurations sensibles :

```env
SECRET_KEY=votre-clé-secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Migrations de la base de données

```bash
python manage.py migrate
```

### 3. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 4. Charger des données de test (optionnel)

```bash
python manage.py loaddata categories products
```

## 🚀 Démarrage

Démarrer le serveur de développement :

```bash
python manage.py runserver
```

L'API sera accessible à : `http://localhost:8000/`
L'interface d'administration : `http://localhost:8000/admin/`

## 📊 Modèles de Données

### Category (Catégorie)
Représente une catégorie de produits.

```
- id (Integer, PK)
- name (CharField, max_length=100)
```

### Product (Produit)
Représente un produit avec un prix et une catégorie.

```
- id (Integer, PK)
- name (CharField, max_length=200)
- price (DecimalField, max_digits=10, decimal_places=2)
- category (ForeignKey → Category)
- available (BooleanField, default=True)
```

### Order (Commande)
Représente une commande pour une table.

```
- id (Integer, PK)
- table_number (IntegerField)
- status (CharField, choices: pending, preparing, ready, delivered, cancelled)
- created_at (DateTimeField, auto_now_add=True)
- updated_at (DateTimeField, auto_now=True)

Méthodes :
- get_total() : Calcule le montant total de la commande
```

**Statuts disponibles :**
- `pending` : En attente
- `preparing` : En préparation
- `ready` : Prêt
- `delivered` : Livré
- `cancelled` : Annulé

### OrderItem (Article de Commande)
Représente un article dans une commande.

```
- id (Integer, PK)
- order (ForeignKey → Order)
- product (ForeignKey → Product)
- quantity (PositiveIntegerField, default=1)
- price (DecimalField, max_digits=10, decimal_places=2)

Méthodes :
- subtotal() : Calcule le sous-total de l'article (quantité × prix)
```

## 🔌 Endpoints API

### Categories
- `GET /api/categories/` - Lister toutes les catégories
- `POST /api/categories/` - Créer une catégorie
- `GET /api/categories/{id}/` - Récupérer une catégorie
- `PUT /api/categories/{id}/` - Mettre à jour une catégorie
- `DELETE /api/categories/{id}/` - Supprimer une catégorie

### Products
- `GET /api/products/` - Lister tous les produits
- `POST /api/products/` - Créer un produit
- `GET /api/products/{id}/` - Récupérer un produit
- `PUT /api/products/{id}/` - Mettre à jour un produit
- `DELETE /api/products/{id}/` - Supprimer un produit

**Filters :**
- `?available=true` - Filtrer par disponibilité
- `?category={id}` - Filtrer par catégorie

### Orders
- `GET /api/orders/` - Lister toutes les commandes
- `POST /api/orders/` - Créer une commande
- `GET /api/orders/{id}/` - Récupérer une commande
- `PUT /api/orders/{id}/` - Mettre à jour une commande
- `DELETE /api/orders/{id}/` - Supprimer une commande
- `PATCH /api/orders/{id}/status/` - Mettre à jour le statut d'une commande
- `POST /api/orders/{id}/add_item/` - Ajouter un article à une commande

**Filters :**
- `?table_number={numero}` - Filtrer par numéro de table
- `?status={status}` - Filtrer par statut

### OrderItems
- `GET /api/orderitems/` - Lister tous les articles
- `POST /api/orderitems/` - Créer un article
- `GET /api/orderitems/{id}/` - Récupérer un article
- `PUT /api/orderitems/{id}/` - Mettre à jour un article
- `DELETE /api/orderitems/{id}/` - Supprimer un article

## 📝 Exemples d'Utilisation

### Créer une catégorie

```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d {
    "name": "Boissons"
  }
```

### Créer un produit

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d {
    "name": "Café",
    "price": "2.50",
    "category": 1,
    "available": true
  }
```

### Créer une commande avec articles

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d {
    "table_number": 5,
    "status": "pending",
    "items": [
      {
        "product": 1,
        "quantity": 2
      },
      {
        "product": 2,
        "quantity": 1
      }
    ]
  }
```

### Mettre à jour le statut d'une commande

```bash
curl -X PATCH http://localhost:8000/api/orders/1/status/ \
  -H "Content-Type: application/json" \
  -d {
    "status": "ready"
  }
```

### Ajouter un article à une commande

```bash
curl -X POST http://localhost:8000/api/orders/1/add_item/ \
  -H "Content-Type: application/json" \
  -d {
    "product": 3,
    "quantity": 1
  }
```

### Filtrer les commandes par statut

```bash
curl http://localhost:8000/api/orders/?status=pending
```

## 🔐 Authentification

L'application utilise **JWT (JSON Web Tokens)** pour l'authentification via le package `djangorestframework-simplejwt`.

### Obtenir un token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d {
    "username": "utilisateur",
    "password": "motdepasse"
  }
```

**Réponse :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Utiliser le token dans les requêtes

```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Rafraîchir un token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
```

## 📁 Structure du Projet

```
django_gestion_commande/
├── manage.py              # Script de gestion Django
├── db.sqlite3             # Base de données
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
│
├── restoProject/         # Configuration du projet
│   ├── __init__.py
│   ├── settings.py       # Paramètres Django
│   ├── urls.py           # Routage URL
│   ├── asgi.py           # Configuration ASGI
│   └── wsgi.py           # Configuration WSGI
│
└── orders/               # Application principale
    ├── models.py         # Modèles de base de données
    ├── views.py          # ViewSets API
    ├── serializers.py    # Sérialiseurs DRF
    ├── admin.py          # Configuration admin
    ├── apps.py           # Configuration app
    ├── tests.py          # Tests unitaires
    ├── migrations/       # Migrations de BD
    └── __pycache__/      # Fichiers compilés Python
```

## 🧪 Tests

Exécuter les tests :

```bash
python manage.py test
```

## 📦 Dépendances

- **Django** (6.0.3) : Framework web
- **djangorestframework** (3.14.0) : Framework REST
- **django-cors-headers** (4.3.1) : Support CORS
- **djangorestframework-simplejwt** (5.3.0) : Authentification JWT
- **django-filter** (23.2) : Filtrage avancé
- **PyMySQL** (1.1.2) : Driver MySQL
- **python-dotenv** (1.2.2) : Gestion des variables d'environnement
- **sqlparse** (0.5.5) : Parsing SQL
- **asgiref** (3.11.1) : Support ASGI

## 🐛 Dépannage

### Erreur de migration

Si vous rencontrez des erreurs lors des migrations :

```bash
# Réinitialiser les migrations
python manage.py migrate zero orders

# Refaire les migrations
python manage.py makemigrations
python manage.py migrate
```

### Problèmes de CORS

Vérifiez que `ALLOWED_HOSTS` et `CORS_ALLOWED_ORIGINS` dans `settings.py` sont correctement configurés pour accueillir les domaines frontend.

### Connexion à la base de données

Assurez-vous que:
- MySQL est en cours d'exécution (si utilisé)
- Les identifiants de connexion sont corrects dans `settings.py`
- La base de données est créée

## 📞 Support et Contribution

Pour toute question ou contribution, veuillez ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT.

---

**Dernière mise à jour :** 31 mars 2026
