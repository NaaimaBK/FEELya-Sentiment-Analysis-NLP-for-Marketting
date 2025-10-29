# FEELya Frontend

Interface React pour le système de recommandation par sentiment FEELya.

## Installation

```bash
# 1. Installer les dépendances
npm install

# 2. Configurer l'API
# Créer un fichier .env avec:
# REACT_APP_API_URL=http://localhost:8000/api/v1

# 3. Lancer l'application
npm start
```

L'application sera disponible sur http://localhost:3000

## Scripts disponibles

- `npm start` - Lance l'application en mode développement
- `npm build` - Compile l'application pour la production
- `npm test` - Lance les tests
- `npm eject` - Éjecte la configuration (non réversible)

## Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.jsx              # Composant racine
│   ├── index.js             # Point d'entrée
│   ├── index.css            # Styles globaux avec Tailwind
│   ├── components/
│   │   └── FEELyaApp.jsx   # Composant principal
│   └── services/
│       └── api.js           # Service API
├── package.json
└── .env
```

## Connexion au Backend

Assurez-vous que le backend FastAPI est lancé sur le port 8000 :

```bash
cd ../backend
uvicorn main:app --reload
```

## Fonctionnalités

- ✅ Dashboard en temps réel avec statistiques
- ✅ Gestion et filtrage des avis clients
- ✅ Analyse de sentiment en direct
- ✅ Système de recommandations
- ✅ Support multilingue (FR/AR/Darija)
- ✅ Interface responsive et moderne