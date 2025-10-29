"""
Script pour initialiser la base de données
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import Base, engine

def init_database():
    """Créer toutes les tables"""
    print("🔧 Création des tables de la base de données...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données initialisée avec succès!")
        print(f"📍 Fichier DB: {engine.url}")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    init_database()