# Guide de Déploiement - AfroNoel sur VPS Ubuntu
# Domaine: tmc.supahuman.site

## Prérequis
- VPS Ubuntu 22.04 ou 24.04
- Accès root ou utilisateur avec privilèges sudo
- Domaine tmc.supahuman.site pointant vers l'IP du VPS (enregistrement DNS A)

---

## ÉTAPE 1 : Connexion au VPS et mise à jour système

\`\`\`bash
# Connexion SSH
ssh root@VOTRE_IP_VPS

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances de base
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    nginx postgresql postgresql-contrib libpq-dev \
    git curl certbot python3-certbot-nginx ufw
\`\`\`

---

## ÉTAPE 2 : Configuration du pare-feu (UFW)

\`\`\`bash
# Activer UFW
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
\`\`\`

---

## ÉTAPE 3 : Création de l'utilisateur pour l'application

\`\`\`bash
# Créer un utilisateur dédié
sudo adduser afronoel
sudo usermod -aG sudo afronoel

# Se connecter en tant qu'afronoel
sudo su - afronoel
\`\`\`

---

## ÉTAPE 4 : Configuration de PostgreSQL

\`\`\`bash
# Se connecter en tant que postgres
sudo -u postgres psql

# Dans le shell PostgreSQL, exécuter :
CREATE DATABASE afronoel_db;
CREATE USER afronoel_user WITH PASSWORD 'VotreMotDePasseSecurise123!';
ALTER ROLE afronoel_user SET client_encoding TO 'utf8';
ALTER ROLE afronoel_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE afronoel_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE afronoel_db TO afronoel_user;
\q
\`\`\`

---

## ÉTAPE 5 : Cloner et configurer le projet

\`\`\`bash
# Créer le répertoire du projet
sudo mkdir -p /var/www/afronoel
sudo chown afronoel:afronoel /var/www/afronoel
cd /var/www/afronoel

# Copier vos fichiers (via SCP depuis votre machine locale)
# Depuis votre machine locale :
# scp -r ./afronoel/* afronoel@VOTRE_IP_VPS:/var/www/afronoel/

# OU cloner depuis un dépôt Git
# git clone https://votre-repo-git.com/afronoel.git .

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
\`\`\`

---

## ÉTAPE 6 : Configuration des variables d'environnement

\`\`\`bash
# Créer le fichier .env
nano /var/www/afronoel/.env
\`\`\`

Contenu du fichier `.env` :
\`\`\`
DEBUG=False
SECRET_KEY=votre-cle-secrete-tres-longue-et-complexe-generee-aleatoirement
ALLOWED_HOSTS=tmc.supahuman.site,www.tmc.supahuman.site

# Base de données PostgreSQL
DATABASE_URL=postgres://afronoel_user:VotreMotDePasseSecurise123!@localhost:5432/afronoel_db

# WhatsApp
WHATSAPP_NUMBER=237XXXXXXXXX
\`\`\`

---

## ÉTAPE 7 : Modifier settings.py pour la production

Modifiez `/var/www/afronoel/afronoel/settings.py` :

\`\`\`python
import os
from pathlib import Path
import dj_database_url

# Charger les variables d'environnement
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-cle-par-defaut')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Base de données PostgreSQL
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}

# Fichiers statiques
STATIC_ROOT = BASE_DIR / 'staticfiles'
\`\`\`

---

## ÉTAPE 8 : Migrations et collecte des fichiers statiques

\`\`\`bash
cd /var/www/afronoel
source venv/bin/activate

# Charger les variables d'environnement
export $(cat .env | xargs)

# Migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Créer le superutilisateur admin
python manage.py createsuperuser
\`\`\`

---

## ÉTAPE 9 : Configuration de Gunicorn (service systemd)

\`\`\`bash
# Créer le fichier de service
sudo nano /etc/systemd/system/afronoel.service
\`\`\`

Contenu du fichier :
\`\`\`ini
[Unit]
Description=AfroNoel Gunicorn Daemon
After=network.target

[Service]
User=afronoel
Group=www-data
WorkingDirectory=/var/www/afronoel
EnvironmentFile=/var/www/afronoel/.env
ExecStart=/var/www/afronoel/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/var/www/afronoel/afronoel.sock \
    afronoel.wsgi:application

[Install]
WantedBy=multi-user.target
\`\`\`

\`\`\`bash
# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl start afronoel
sudo systemctl enable afronoel
sudo systemctl status afronoel
\`\`\`

---

## ÉTAPE 10 : Configuration de Nginx

\`\`\`bash
# Copier le fichier de configuration Nginx
sudo cp /var/www/afronoel/nginx/afronoel.conf /etc/nginx/sites-available/afronoel

# Activer le site
sudo ln -s /etc/nginx/sites-available/afronoel /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
\`\`\`

---

## ÉTAPE 11 : Installation du certificat SSL (Let's Encrypt)

\`\`\`bash
# Obtenir le certificat SSL
sudo certbot --nginx -d tmc.supahuman.site -d www.tmc.supahuman.site

# Suivre les instructions à l'écran
# Choisir de rediriger HTTP vers HTTPS (option 2)

# Vérifier le renouvellement automatique
sudo certbot renew --dry-run
\`\`\`

---

## ÉTAPE 12 : Permissions finales

\`\`\`bash
# Permissions sur le socket et les fichiers
sudo chown -R afronoel:www-data /var/www/afronoel
sudo chmod -R 755 /var/www/afronoel
sudo chmod 660 /var/www/afronoel/afronoel.sock
\`\`\`

---

## Commandes utiles

\`\`\`bash
# Voir les logs de l'application
sudo journalctl -u afronoel -f

# Redémarrer l'application après modifications
sudo systemctl restart afronoel

# Voir les logs Nginx
sudo tail -f /var/log/nginx/afronoel_error.log
sudo tail -f /var/log/nginx/afronoel_access.log

# Vérifier le statut des services
sudo systemctl status afronoel
sudo systemctl status nginx
sudo systemctl status postgresql

# Mettre à jour le code (après git pull ou nouveau upload)
cd /var/www/afronoel
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart afronoel
\`\`\`

---

## Dépannage

### Erreur 502 Bad Gateway
\`\`\`bash
# Vérifier que Gunicorn tourne
sudo systemctl status afronoel

# Vérifier les permissions du socket
ls -la /var/www/afronoel/afronoel.sock

# Redémarrer les services
sudo systemctl restart afronoel
sudo systemctl restart nginx
\`\`\`

### Erreur de base de données
\`\`\`bash
# Vérifier PostgreSQL
sudo systemctl status postgresql

# Tester la connexion
psql -h localhost -U afronoel_user -d afronoel_db
\`\`\`

### Fichiers statiques non chargés
\`\`\`bash
# Re-collecter les fichiers statiques
cd /var/www/afronoel
source venv/bin/activate
python manage.py collectstatic --noinput

# Vérifier les permissions
sudo chown -R afronoel:www-data /var/www/afronoel/staticfiles
\`\`\`

---

## Résumé des accès

- **Site public** : https://tmc.supahuman.site
- **Admin Django** : https://tmc.supahuman.site/admin/
- **Fichiers du projet** : /var/www/afronoel/
- **Logs Gunicorn** : `sudo journalctl -u afronoel -f`
- **Logs Nginx** : /var/log/nginx/afronoel_*.log
