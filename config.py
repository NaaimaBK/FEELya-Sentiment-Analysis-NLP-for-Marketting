import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Settings:
    # Database - utiliser SQLite par défaut pour faciliter le développement
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feelya.db")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # ML Models
    SENTIMENT_MODEL_FR = "camembert-base"
    SENTIMENT_MODEL_AR = "aubmindlab/bert-base-arabertv2"
    
    # Scraping
    SCRAPING_USER_AGENT = "FEELya-Bot/1.0"
    SCRAPING_DELAY = 2
    
    # Recommandation
    MIN_REVIEWS_FOR_RECOMMENDATION = 5
    RECOMMENDATION_TOP_N = 10

settings = Settings()
