# AfroNoël - Site E-commerce Django

## Installation

1. Créer un environnement virtuel :
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
\`\`\`

2. Installer les dépendances :
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Appliquer les migrations :
\`\`\`bash
python manage.py migrate
\`\`\`

4. Créer un superutilisateur :
\`\`\`bash
python manage.py createsuperuser
\`\`\`

5. Lancer le serveur :
\`\`\`bash
python manage.py runserver
\`\`\`

6. Accéder au site :
- Frontend : http://localhost:8000
- Admin : http://localhost:8000/admin

## Configuration WhatsApp

Modifiez le numéro WhatsApp dans `afronoel/settings.py` :
\`\`\`python
WHATSAPP_NUMBER = "237600000000"  # Votre numéro
