# 🍽️ Django Gestion de Commandes — API REST

**Django 6.0.3** · **DRF 3.14.0** · **SimpleJWT 5.3.0** · **SQLite / MySQL**

---

## Prérequis

- Python 3.8+
- pip

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver       # → http://localhost:8000
```

## Variables d'environnement

Créer un fichier `.env` à la racine :

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

## Dépendances

```
asgiref==3.11.1
Django==6.0.3
PyMySQL==1.1.2
sqlparse==0.5.5
djangorestframework==3.14.0
django-cors-headers==4.3.1
djangorestframework-simplejwt==5.3.0
django-filter==23.2
python-dotenv==1.2.2
```

---

## Endpoints — Base URL : `/api/`

| Ressource | Endpoints |
|-----------|-----------|
| Catégories | `/categories/` |
| Produits | `/products/` · `?available=true` · `?category={id}` |
| Tables | `/tables/` |
| Clients | `/clients/` |
| Réservations | `/reservations/` · `/reservations/confirm/<uuid>/` |
| Commandes | `/orders/` · `/orders/{id}/status/` · `?table={id}` · `?status=...` |
| Articles | `/orderitems/` |
| Auth JWT | `/token/` · `/token/refresh/` |

Toutes les ressources supportent GET / POST / PUT / PATCH / DELETE.

---

## Authentification

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Utiliser le token
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Modèles

| Modèle | Champs clés |
|--------|-------------|
| `Category` | name |
| `Product` | name, price, category, available |
| `Table` | number, capacity, status (`free`/`occuped`) |
| `Client` | nom, adresse, telephone, email |
| `Reservation` | date_heure, nb_personnes, statut, type_commande, client, table, token_confirmation |
| `Order` | table, client, reservation, type_commande, status, items, total |
| `OrderItem` | order, product, quantity, price |

**Statuts commande :** `pending` → `preparing` → `ready` → `delivered` / `cancelled`

**Types commande :** `on_site` · `take_away` · `online`

---

## Logique métier

- **Option B** : si une commande `pending` existe pour la même table, les nouveaux articles y sont ajoutés automatiquement.
- Le statut de la table passe à `occuped` à la création d'une commande, et à `free` à la livraison.
- La création d'une réservation envoie un email de confirmation avec un lien UUID.

---

## Dépannage

```bash
# Erreur de migration
python manage.py migrate zero orders
python manage.py makemigrations && python manage.py migrate

# Port déjà utilisé
python manage.py runserver 8001
```