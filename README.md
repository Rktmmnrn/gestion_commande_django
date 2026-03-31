# Django Gestion de Commandes

Une application Django REST Framework pour gérer les commandes et produits d'un restaurant. Cette API permet de créer, consulter et gérer les commandes, les produits, les catégories et les détails des commandes.

## 📋 Caractéristiques

- **Gestion des catégories** : Créer et organiser les catégories de produits
- **Gestion des produits** : Ajouter et gérer les produits avec prix et disponibilité
- **Gestion des commandes** : Créer des commandes pour les tables avec statut
- **Détails des commandes** : Ajouter des articles aux commandes
- **Filtrage avancé** : Filtrer les commandes et produits par différents critères
- **Authentification JWT** : Sécurisation de l'API avec les tokens JWT
- **CORS activé** : Support du cross-origin pour les requêtes frontend
- **API RESTful** : Architecture REST complète avec HTTP standards

## 🛠️ Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- MySQL ou SQLite (pour la base de données)

## 📦 Installation

### 1. Cloner ou configurer le projet

```bash
cd django_gestion_commande
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

### 3. Activer l'environnement virtuel

**Sur Linux/macOS :**
```bash
source .venv/bin/activate
```

**Sur Windows :**
```bash
.venv\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
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
