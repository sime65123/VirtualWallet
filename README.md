# VirtualWallet - Système de Gestion de Lavage Auto

Une application web Django pour la gestion des services de lavage automobile avec un système de portefeuille virtuel intégré.

## Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Technologies utilisées](#technologies-utilisées)

## Aperçu

VirtualWallet est une application web qui permet aux clients de s'inscrire, de recharger leur compte virtuel et de souscrire à des services de lavage automobile. L'application gère l'authentification des utilisateurs, les transactions financières et les réservations de services.

## Fonctionnalités

- **Authentification des utilisateurs** :
  - Inscription avec vérification par email
  - Connexion/déconnexion
  - Gestion de profil utilisateur

- **Système de portefeuille virtuel** :
  - Recharge de compte
  - Suivi des transactions
  - Paiement des services

- **Services de lavage automobile** :
  - Différents forfaits de lavage (simple, complet, premium, à sec)
  - Souscription aux services
  - Historique des services utilisés

- **Vitrine du service** :
  - Présentation des services
  - Galerie de photos
  - Témoignages clients
  - Formulaire de contact

## Prérequis

- Python 3.8 ou supérieur
- Django 3.2 ou supérieur
- Base de données (MySQL, PostgreSQL ou SQLite)
- Serveur SMTP pour l'envoi d'emails (pour la vérification des comptes)
- Autres dépendances listées dans `requirements.txt`

## Installation

1. **Cloner le dépôt**
   ```
   git clone https://github.com/sime65123/VirtualWallet.git
   cd VirtualWallet
   ```

2. **Créer un environnement virtuel**
   ```
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Installer les dépendances**
   ```
   pip install -r requirements.txt
   ```

5. **Configurer la base de données**
   - Créer une base de données dans MySQL ou PostgreSQL
   - Configurer les paramètres de connexion dans `settings.py` (voir section Configuration)

6. **Appliquer les migrations**
   ```
   python manage.py migrate
   ```

7. **Créer un superutilisateur (administrateur)**
   ```
   python manage.py createsuperuser
   ```

8. **Collecter les fichiers statiques**
   ```
   python manage.py collectstatic
   ```

## Configuration

1. **Configuration de la base de données**
   - Ouvrir le fichier `VirtualWallet/settings.py`
   - Modifier les paramètres de connexion à la base de données:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',  # ou 'django.db.backends.postgresql'
             'NAME': 'nom_de_votre_base_de_donnees',
             'USER': 'votre_utilisateur',
             'PASSWORD': 'votre_mot_de_passe',
             'HOST': 'localhost',
             'PORT': '3306',  # '5432' pour PostgreSQL
         }
     }
     ```

2. **Configuration des emails**
   - Configurer les paramètres SMTP dans `settings.py`:
     ```python
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     EMAIL_HOST = 'smtp.votre-service-email.com'
     EMAIL_PORT = 587
     EMAIL_USE_TLS = True
     EMAIL_HOST_USER = 'votre-email@exemple.com'
     EMAIL_HOST_PASSWORD = 'votre-mot-de-passe'
     DEFAULT_FROM_EMAIL = 'VirtualWallet <votre-email@exemple.com>'
     ```

3. **Variables d'environnement (recommandé)**
   - Créer un fichier `.env` à la racine du projet
   - Définir les variables sensibles (clés secrètes, identifiants de base de données, etc.)
   - Utiliser `python-dotenv` pour charger ces variables

## Utilisation

1. **Lancer le serveur de développement**
   ```
   python manage.py runserver
   ```

2. **Accéder à l'application**
   - Ouvrir un navigateur web
   - Accéder à l'URL: `http://localhost:8000/emailApp/vitrine`

3. **Inscription et activation**
   - Créer un compte utilisateur via la page d'inscription
   - Vérifier votre email pour activer le compte
   - Se connecter avec les identifiants créés

4. **Recharger votre compte**
   - Accéder à l'option "Recharge Compte" dans le menu utilisateur
   - Saisir les informations de paiement
   - Confirmer la transaction

5. **Souscrire à un service de lavage**
   - Sélectionner "Souscription Lavage" dans le menu utilisateur
   - Choisir le forfait souhaité
   - Confirmer la souscription

6. **Administration**
   - Accéder à l'interface d'administration: `http://localhost:8000/admin`
   - Se connecter avec les identifiants superutilisateur
   - Gérer les utilisateurs, transactions et services

## Structure du projet

```
VirtualWallet/
├── VirtualWallet/            # Configuration principale du projet
│   ├── settings.py           # Paramètres du projet
│   ├── urls.py               # Configuration des URLs principales
│   └── wsgi.py               # Configuration WSGI
├── emailApp/                 # Application de gestion des emails et authentification
│   ├── models.py             # Modèles de données
│   ├── views.py              # Vues et logique métier
│   └── urls.py               # Configuration des URLs de l'application
├── templates/                # Templates HTML
│   ├── base.html             # Template de base
│   ├── vitrine.html          # Page d'accueil/vitrine
│   └── ...                   # Autres templates
├── static/                   # Fichiers statiques (CSS, JS, images)
│   └── assets/               # Ressources du site
├── media/                    # Fichiers téléchargés par les utilisateurs
├── manage.py                 # Script de gestion Django
└── requirements.txt          # Liste des dépendances
```

## Technologies utilisées

- **Backend**:
  - Django (framework web Python)
  - Django REST Framework (si utilisé pour des API)

- **Frontend**:
  - Bootstrap (framework CSS)
  - jQuery (bibliothèque JavaScript)
  - Swiper (pour les sliders)
  - Font Awesome et Ionicons (pour les icônes)

- **Base de données**:
  - MySQL ou PostgreSQL

- **Autres**:
  - SMTP pour l'envoi d'emails
  - Python-dotenv pour la gestion des variables d'environnement
