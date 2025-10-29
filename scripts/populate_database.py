import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from models.database import SessionLocal, Product, Review, User
from services.preprocessor import TextPreprocessor
from services.sentiment_analyzer import SentimentAnalyzer
import random
from datetime import datetime, timedelta

def create_sample_data():
    print("🚀 Démarrage du peuplement de la base de données...")
    
    db = SessionLocal()
    preprocessor = TextPreprocessor()
    sentiment_analyzer = SentimentAnalyzer()
    
    # Créer des utilisateurs
    print("👥 Création des utilisateurs...")
    users = []
    for i in range(20):
        user = User(
            username=f"user{i+1}",
            email=f"user{i+1}@example.com",
            hashed_password="hashed_password_here"
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"   ✓ {len(users)} utilisateurs créés")
    
    # Créer des produits
    print("📦 Création des produits...")
    products_data = [
        {
            "name": "Smartphone Samsung Galaxy S23",
            "category": "Électronique",
            "description": "Dernier smartphone Samsung avec 5G",
            "price": 8999.00,
            "platform": "jumia"
        },
        {
            "name": "Laptop HP Pavilion 15",
            "category": "Informatique",
            "description": "Ordinateur portable performant pour le travail",
            "price": 6499.00,
            "platform": "jumia"
        },
        {
            "name": "Machine à café Nespresso",
            "category": "Électroménager",
            "description": "Cafetière automatique avec capsules",
            "price": 1299.00,
            "platform": "hmizate"
        },
        {
            "name": "Nike Air Max 270",
            "category": "Chaussures",
            "description": "Chaussures de sport confortables",
            "price": 1199.00,
            "platform": "jumia"
        },
        {
            "name": "Apple Watch Series 8",
            "category": "Électronique",
            "description": "Montre connectée avec GPS",
            "price": 4999.00,
            "platform": "jumia"
        },
        {
            "name": "Sony WH-1000XM5",
            "category": "Audio",
            "description": "Casque sans fil à réduction de bruit",
            "price": 3499.00,
            "platform": "hmizate"
        },
        {
            "name": "Dyson V11 Aspirateur",
            "category": "Électroménager",
            "description": "Aspirateur sans fil puissant",
            "price": 5999.00,
            "platform": "jumia"
        },
        {
            "name": "Canon EOS R6",
            "category": "Photo",
            "description": "Appareil photo hybride professionnel",
            "price": 24999.00,
            "platform": "hmizate"
        }
    ]
    
    products = []
    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)
        products.append(product)
    
    db.commit()
    print(f"   ✓ {len(products)} produits créés")
    
    # Créer des avis
    print("💬 Création des avis...")
    reviews_templates = {
        'positive_fr': [
            "Excellent produit, très satisfait de mon achat !",
            "Qualité au top, je recommande vivement",
            "Parfait, exactement ce que je cherchais",
            "Super rapport qualité-prix, livraison rapide",
            "Produit de très bonne qualité, conforme à la description"
        ],
        'negative_fr': [
            "Déçu par la qualité, pas comme sur la photo",
            "Service client médiocre, problème non résolu",
            "Le produit est arrivé endommagé",
            "Prix trop élevé pour cette qualité",
            "Ne fonctionne pas correctement"
        ],
        'neutral_fr': [
            "Produit correct, rien d'exceptionnel",
            "Conforme à la description",
            "Bien mais pourrait être amélioré",
            "Satisfait dans l'ensemble",
            "Prix un peu élevé mais qualité correcte"
        ],
        'positive_ar': [
            "منتج ممتاز، أنصح به بشدة",
            "جودة عالية، راضي جدا",
            "رائع، بالضبط ما كنت أبحث عنه",
            "توصيل سريع ومنتج مطابق",
            "جودة ممتازة"
        ],
        'negative_ar': [
            "غير راضي عن الجودة",
            "المنتج وصل تالف",
            "خدمة العملاء سيئة",
            "السعر مرتفع",
            "لا يعمل بشكل صحيح"
        ]
    }
    
    total_reviews = 0
    for product in products:
        num_reviews = random.randint(10, 30)
        
        for _ in range(num_reviews):
            sentiment_type = random.choices(
                ['positive', 'neutral', 'negative'],
                weights=[0.6, 0.25, 0.15]
            )[0]
            
            language = random.choices(['fr', 'ar'], weights=[0.7, 0.3])[0]
            
            if sentiment_type == 'positive':
                review_text = random.choice(reviews_templates[f'positive_{language}'])
                rating = random.uniform(4.0, 5.0)
            elif sentiment_type == 'neutral':
                if language == 'ar':
                    review_text = random.choice(reviews_templates['positive_ar'])
                else:
                    review_text = random.choice(reviews_templates['neutral_fr'])
                rating = random.uniform(2.5, 3.9)
            else:
                review_text = random.choice(reviews_templates[f'negative_{language}'])
                rating = random.uniform(1.0, 2.4)
            
            processed_text, detected_lang = preprocessor.preprocess(review_text)
            sentiment_result = sentiment_analyzer.analyze(processed_text, detected_lang)
            
            review = Review(
                user_id=random.choice(users).id,
                product_id=product.id,
                rating=round(rating, 1),
                text=review_text,
                language=detected_lang,
                sentiment=sentiment_result['sentiment'],
                sentiment_score=sentiment_result['sentiment_score'],
                confidence=sentiment_result['confidence'],
                processed=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            db.add(review)
            total_reviews += 1
        
        db.commit()
        
        # Mettre à jour les stats du produit
        all_reviews = db.query(Review).filter(Review.product_id == product.id).all()
        
        product.total_reviews = len(all_reviews)
        product.positive_reviews = sum(1 for r in all_reviews if r.sentiment == 'Positif')
        product.neutral_reviews = sum(1 for r in all_reviews if r.sentiment == 'Neutre')
        product.negative_reviews = sum(1 for r in all_reviews if r.sentiment == 'Négatif')
        
        if all_reviews:
            product.avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
            product.sentiment_score = sum(r.sentiment_score for r in all_reviews) / len(all_reviews)
        
        db.commit()
        print(f"   ✓ Produit '{product.name}': {len(all_reviews)} avis")
    
    print(f"\n✅ Base de données peuplée avec succès!")
    print(f"   📊 Résumé:")
    print(f"      - {len(users)} utilisateurs")
    print(f"      - {len(products)} produits")
    print(f"      - {total_reviews} avis")
    
    db.close()

if __name__ == "__main__":
    create_sample_data()
