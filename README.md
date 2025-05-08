# BueaDelights
# BueaDelights 🍕🍹

> "Des saveurs locales à portée de clic"

BueaDelights est une application web vitrine conçue pour permettre à un jeune entrepreneur camerounais basé à Buea de présenter, promouvoir et vendre ses produits alimentaires locaux. L'application est optimisée pour le contexte camerounais, en tenant compte des contraintes locales comme la bande passante, les méthodes de paiement disponibles et les habitudes de consommation.

![BueaDelights Logo](static/images/logo.png)

## 📋 Fonctionnalités

- **Vitrine des produits** : Présentation attrayante des produits alimentaires locaux
- **Catalogue de produits** : Classés par catégories avec photos, descriptions et prix
- **Système de commande** : Panier d'achat intuitif et processus simplifié
- **Réservations** : Possibilité de réserver des produits à l'avance
- **Paiements locaux** : Intégration avec Mobile Money et Orange Money
- **Espace client** : Création de compte, historique des commandes, programme de fidélité
- **Administration** : Interface simplifiée pour gérer les produits, commandes et clients

## 🚀 Installation

### Prérequis

- Python 3.9+
- pip
- virtualenv
- Node.js et npm (pour Tailwind CSS)

### Configuration de l'environnement

1. **Cloner le dépôt**

```bash
git clone https://github.com/votre-utilisateur/buea-delights.git
cd buea-delights
```

2. **Créer et activer un environnement virtuel**

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (macOS/Linux)
source venv/bin/activate
```

3. **Installer les dépendances**

```bash
# Installer les packages Python
pip install -r requirements.txt

# Installer les dépendances Node.js pour Tailwind
python manage.py tailwind install
```

4. **Configurer les variables d'environnement**

Créez un fichier `.env` à la racine du projet avec les variables suivantes:

```
DEBUG=True
SECRET_KEY=votre-clé-secrète-ici
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

5. **Appliquer les migrations**

```bash
python manage.py migrate
```

6. **Créer un superutilisateur**

```bash
python manage.py createsuperuser
```

## 💻 Lancement de l'application

1. **Démarrer Tailwind CSS en mode développement**

```bash
python manage.py tailwind start
```

2. **Lancer le serveur de développement Django**

Dans un nouveau terminal (avec l'environnement virtuel activé):

```bash
python manage.py runserver
```

3. **Accéder à l'application**

Ouvrez votre navigateur et accédez à:
- Application: http://127.0.0.1:8000/
- Administration: http://127.0.0.1:8000/admin/

## 📁 Structure du projet

```
buea_project/
├── buea/                   # Configuration du projet
│   ├── settings.py         # Paramètres du projet
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuration WSGI
├── backed/                 # Application principale
│   ├── templates/          # Templates spécifiques à l'app
│   ├── static/             # Fichiers statiques de l'app
│   ├── migrations/         # Migrations de base de données
│   ├── admin.py            # Configuration de l'interface admin
│   ├── models.py           # Modèles de données
│   ├── urls.py             # URLs de l'application
│   └── views.py            # Vues de l'application
├── templates/              # Templates à l'échelle du projet
│   └── base.html           # Template de base
├── static/                 # Fichiers statiques du projet
│   ├── css/                # Fichiers CSS
│   ├── js/                 # Fichiers JavaScript
│   └── images/             # Images
├── theme/                  # Application Tailwind CSS
├── .env                    # Variables d'environnement
├── .gitignore              # Configuration Git
├── requirements.txt        # Dépendances Python
└── manage.py               # Script de gestion Django
```

## 🔧 Technologies utilisées

- **Backend**: Django
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Base de données**: SQLite (dev), PostgreSQL (prod)
- **Déploiement**: Render
- **Autres**:
  - django-tailwind pour l'intégration de Tailwind CSS
  - django-browser-reload pour le hot reloading pendant le développement

## 🌐 Déploiement

L'application est configurée pour être déployée sur Render:

1. Connectez votre dépôt GitHub à Render
2. Créez un nouveau service Web
3. Utilisez les paramètres suivants:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn buea.wsgi:application`
4. Configurez les variables d'environnement nécessaires

## 🤝 Contribuer

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commitez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📝 Roadmap

- Application mobile native
- Système de livraison avec suivi en temps réel
- Expansion vers d'autres villes camerounaises
- Fonctionnalités sociales (partage de photos, avis)
- Système de fidélité avancé

## 📜 Licence

Ce projet est sous licence [MIT](LICENSE)

## 👥 À propos

BueaDelights est un projet développé pour soutenir les entrepreneurs locaux à Buea, Cameroun, en leur offrant une plateforme numérique pour présenter et vendre leurs produits alimentaires artisanaux.

---

ngrok http 8000




Développé avec ❤️ pour l'entreprenariat camerounais