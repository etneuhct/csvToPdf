# csvToPdf

## Premiers pas
a) Récupérer le dépôt
```bash
git clone https://github.com/etneuhct/csvToPdf
cd csvToPdf
```

b) Installer les dépendances
```bash
pip install -r requirements.txt
```
c) Configurer SendGrid
- Se créer un compte et générer un token : https://sendgrid.com/
- Renseigner et valider un mail d'envoi

d) Configurer Pdfkit
- Installer wkhtmltopdf https://pypi.org/project/pdfkit/

e) Environnement (dans un fichier .env)
- SENDGRID_API_KEY : La clé API fournie par SendGrid
- SENDGRID_ADMIN_MAIL : le mail renseigné dans la configuration SendGrid

You're good to go !

## Description

Ce programme permet de générer des fichiers pdf à partir d'un fichier .csv
Les fichiers ainsi générés sont envoyés aux utilisateurs dont le mail est renseigné
dans ledit fichier
