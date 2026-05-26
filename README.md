# 🎓 Orientation STIM

**Plateforme web d'orientation scolaire pour les nouveaux bacheliers du Bénin**

Une plateforme intelligente qui aide les étudiants bacheliers à trouver l'école ou l'université idéale selon leurs aptitudes et leurs aspirations académiques.

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Stack Technologique](#-stack-technologique)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

### 🎯 Fonctionnalités Principales

- **Recherche d'Écoles et Universités** - Consultez la base de données complète des établissements
- **Fiches Détaillées** - Informations complètes sur chaque établissement (programmes, localisation, contact)
- **Simulateur d'Orientation** - Outil intelligent pour recommander les meilleures options
- **Recherche Globale** - Recherchez rapidement par keywords, région, domaine d'études
- **Gestion de Compte** - Inscription, connexion, profil utilisateur
- **Blog Informatif** - Conseils et actualités sur l'orientation scolaire
- **Système d'Interactions** - Commentaires, notifications, système de notifications

### 🎨 Interface Utilisateur

- Design moderne et responsive
- Styles SCSS personnalisés
- Framework Material Design Bootstrap (MDB)
- Images optimisées via Cloudinary

---

## 🛠️ Stack Technologique

### Backend

| Technologie | Utilisation |
|-------------|-------------|
| **Django 3.2+** | Framework web Python |
| **PostgreSQL** | Base de données (production) / SQLite3 (développement) |
| **Gunicorn** | Serveur WSGI pour production |
| **Whitenoise** | Serveur de fichiers statiques en production |
| **Psycopg2** | Driver PostgreSQL |

### Frontend

| Technologie | Utilisation |
|-------------|-------------|
| **SCSS** | Préprocesseur CSS |
| **HTML5** | Structure |
| **JavaScript** | Interactivité |
| **Material Design Bootstrap** | Framework CSS |

### Services Cloud

| Service | Utilisation |
|---------|-------------|
| **Cloudinary** | Stockage et optimisation d'images |
| **PythonAnywhere** | Hébergement (actuel) |

---

## 📦 Prérequis

Avant de commencer, assure-toi d'avoir installé:

- **Python 3.8+** - [Télécharger](https://www.python.org/downloads/)
- **pip** - Gestionnaire de paquets Python
- **Git** - [Télécharger](https://git-scm.com/)
- **PostgreSQL** (optionnel, pour la production)

### Vérifier les installations

```bash
python --version      # Doit afficher Python 3.8+
pip --version         # Doit afficher pip
git --version         # Doit afficher git
```

---

## 🚀 Installation

### 1️⃣ Cloner le repository

```bash
git clone https://github.com/Ambroise562/orientation-stim.git
cd orientation-stim
```

### 2️⃣ Créer un environnement virtuel

```bash
# Sous Windows
python -m venv venv
venv\Scripts\activate

# Sous macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet:

```bash
cp .env.example .env  # Si le fichier existe
# Ou créer manuellement:
```

Voir la section [Configuration](#-configuration) pour les variables requises.

### 5️⃣ Initialiser la base de données

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (admin)
python manage.py createsuperuser
```

### 6️⃣ Lancer le serveur de développement

```bash
python manage.py runserver
```

L'application est maintenant accessible à: http://localhost:8000

---

## ⚙️ Configuration

### Variables d'Environnement (`.env`)

Crée un fichier `.env` à la racine avec les variables suivantes:

```env
# Django
DJANGO_SECRET_KEY=votre-cle-secrete-generee-aleatoirement
DEBUG=True  # False en production
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com

# Base de données (Développement)
# Pour SQLite3, pas de configuration nécessaire

# Base de données (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/orientation_db

# Cloudinary (Images et média)
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Configuration de site
SITE_URL=http://localhost:8000
SITE_NAME=Orientation STIM
```

### Générer une clé secrète Django

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Configuration Cloudinary (Important!)

1. Créer un compte sur [Cloudinary](https://cloudinary.com/)
2. Récupérer vos identifiants dans le dashboard
3. Ajouter les variables d'environnement
4. Vérifier que `django-cloudinary-storage` est configuré dans `settings.py`

---

## 🎮 Utilisation

### Commandes Utiles

```bash
# Lancer le serveur
python manage.py runserver

# Créer un utilisateur admin
python manage.py createsuperuser

# Créer une nouvelle migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Accéder à l'admin Django
# http://localhost:8000/admin

# Collecter les fichiers statiques (production)
python manage.py collectstatic

# Exécuter les tests
python manage.py test

# Vider le cache
python manage.py clear_cache
```

### Accès Admin

1. Aller sur http://localhost:8000/admin
2. Se connecter avec les identifiants du superutilisateur créé lors de l'installation
3. Ajouter des écoles, universités, et contenu de blog

### Navigation Principale

- **Accueil** - http://localhost:8000/
- **Universités** - http://localhost:8000/universites/
- **Simulateur d'orientation** - http://localhost:8000/simulateur
- **Recherche globale** - http://localhost:8000/recherche_globale
- **Connexion** - http://localhost:8000/comptes/connexion/
- **Panel Admin** - http://localhost:8000/admin/

---

## 🏗️ Architecture

### Structure du Projet

```
orientation-stim/
├── orientation/                 # Configuration principale Django
│   ├── settings.py             # Paramètres Django
│   ├── urls.py                 # Routes principales
│   ├── wsgi.py                 # Configuration WSGI
│   └── asgi.py                 # Configuration ASGI
│
├── blog/                        # App Blog
│   ├── models.py               # Modèles (Posts, Commentaires)
│   ├── views.py                # Vues (affichage du contenu)
│   ├── urls.py                 # Routes blog
│   ├── admin.py                # Configuration admin
│   └── templates/              # Templates HTML
│
├── comptes/                     # App Gestion de Comptes
│   ├── models.py               # Modèles (User, Profil)
│   ├── views.py                # Vues (connexion, inscription)
│   ├── urls.py                 # Routes comptes
│   └── templates/              # Templates HTML
│
├── ecoles/                      # App Écoles
│   ├── models.py               # Modèles (Écoles)
│   └── views.py                # Vues (détails écoles)
│
├── universites/                 # App Universités
│   ├── models.py               # Modèles (Universités)
│   └── views.py                # Vues (détails universités)
│
├── profils/                     # App Profils Utilisateur
│   ├── models.py               # Modèles (Profil)
│   └── views.py                # Vues (profil utilisateur)
│
├── interactions/                # App Interactions
│   ├── models.py               # Modèles (Commentaires, Notifications)
│   ├── views.py                # Vues (interactions)
│   ├── compteur.py             # Logique des notifications
│   └── urls.py                 # Routes interactions
│
├── static/                      # Fichiers statiques
│   ├── css/                    # Styles SCSS/CSS
│   ├── js/                     # JavaScript
│   ├── img/                    # Images
│   └── index.html              # Page statique
│
├── templates/                   # Templates HTML principaux
│   ├── base.html               # Template de base
│   ├── home.html               # Accueil
│   └── ...
│
├── manage.py                    # Gestionnaire Django
├── requirements.txt             # Dépendances Python
├── Procfile                     # Configuration Heroku/production
├── .gitignore                   # Fichiers à ignorer
└── db.sqlite3                   # Base de données développement

```

### Modèles Principaux (Database)

```
User (Django Auth)
├── Profile (1-to-1)
│   ├── avatar (Cloudinary)
│   ├── bio
│   └── preferences

Université
├── name
├── location
├── description
├── image (Cloudinary)
├── programs[]
└── contact

École
├── name
├── location
├── description
├── image (Cloudinary)
└── contact

BlogPost
├── title
├── author (User)
├── content
├── created_at
├── updated_at
└── comments[]

Comment
├── author (User)
├── post (BlogPost)
├── content
├── created_at
```

---

## 🤝 Contribution

Nous accueillons les contributions! Pour contribuer:

### 1. Fork le repository

```bash
git clone https://github.com/YOUR_USERNAME/orientation-stim.git
```

### 2. Créer une branche pour ta feature

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 3. Faire tes modifications

- Respecter les normes de code Django
- Ajouter des tests si possible
- Documenter les changements

### 4. Commit et Push

```bash
git add .
git commit -m "Ajouter: description brève de la modification"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 5. Créer une Pull Request

Ouvrir une PR sur le repository original avec une description claire.

### Normes de Code

- Suivre [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utiliser des noms explicites pour variables et fonctions
- Ajouter des docstrings
- Commenter le code complexe

---

## 🐛 Dépannage

### Problème: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Problème: "Port 8000 déjà utilisé"

**Solution:**
```bash
python manage.py runserver 8001  # Utiliser un autre port
```

### Problème: Erreur de migration

**Solution:**
```bash
python manage.py migrate --fake-initial
```

### Problème: Images ne s'affichent pas

**Solution:**
- Vérifier que Cloudinary est configuré correctement
- Vérifier les variables d'environnement
- Vérifier les permissions Cloudinary

---

## 📚 Ressources Utiles

- [Documentation Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Cloudinary](https://cloudinary.com/documentation)
- [Material Design Bootstrap](https://mdbootstrap.com/docs/standard/)
- [PEP 8 - Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

**Ambroise562**
- GitHub: [@Ambroise562](https://github.com/Ambroise562)
- Email: [ambroisehoundagnanme@gmail.com]
- Site: [sedjro.pythonanywhere.com]

---

## 🙏 Remerciements

- Merci à tous les contributeurs
- Merci à la communauté Django
- Merci aux utilisateurs pour leurs retours

---

## 📞 Support

Pour toute question ou problème:

1. Consulter la section [Dépannage](#-dépannage)
2. Créer une [Issue](https://github.com/Ambroise562/orientation-stim/issues)
3. Rejoindre la communauté

---

## 🔄 Mises à Jour

**Dernière mise à jour:** 26 Mai 2026

### Changelog

- ✅ Documentation README complète
- ✅ Configuration de base Django
- ✅ Intégration Cloudinary
- ⏳ Tests unitaires (en cours)
- ⏳ API REST (planifié)

---

**Bienvenue dans Orientation STIM! 🎉**

Aidons les jeunes bacheliers du Bénin à trouver leur voie! 🚀
