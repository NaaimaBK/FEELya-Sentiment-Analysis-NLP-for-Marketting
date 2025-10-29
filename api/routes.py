from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc  # IMPORTATION CORRIGÉE
from typing import List
from models.database import get_db, Product, Review, User
from models.schemas import (
    ReviewCreate, ReviewResponse,
    ProductCreate, ProductResponse,
    SentimentAnalysisRequest, SentimentAnalysisResponse,
    RecommendationResponse
)
from services.preprocessor import TextPreprocessor
from services.sentiment_analyzer import SentimentAnalyzer
from services.recommender import RecommendationEngine

router = APIRouter()

# Initialiser les services
preprocessor = TextPreprocessor()
sentiment_analyzer = SentimentAnalyzer()
recommender = RecommendationEngine()


@router.post("/reviews/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Créer un nouvel avis et analyser son sentiment"""
    try:
        # Prétraiter le texte
        processed_text, language = preprocessor.preprocess(review.text)
        
        # Analyser le sentiment
        sentiment_result = sentiment_analyzer.analyze(processed_text, language)
        
        # Créer l'avis
        db_review = Review(
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            text=review.text,
            language=language,
            sentiment=sentiment_result['sentiment'],
            sentiment_score=sentiment_result['sentiment_score'],
            confidence=sentiment_result['confidence'],
            processed=True
        )
        
        db.add(db_review)
        
        # Mettre à jour les statistiques du produit
        product = db.query(Product).filter(Product.id == review.product_id).first()
        if product:
            product.total_reviews += 1
            if sentiment_result['sentiment'] == 'Positif':
                product.positive_reviews += 1
            elif sentiment_result['sentiment'] == 'Neutre':
                product.neutral_reviews += 1
            else:
                product.negative_reviews += 1
            
            # Recalculer le score de sentiment moyen
            all_reviews = db.query(Review).filter(Review.product_id == product.id).all()
            if all_reviews:
                avg_sentiment = sum(r.sentiment_score for r in all_reviews) / len(all_reviews)
                product.sentiment_score = avg_sentiment
                
                # Recalculer la note moyenne
                avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
                product.avg_rating = avg_rating
        
        db.commit()
        db.refresh(db_review)
        
        return db_review
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'avis: {str(e)}")


@router.get("/reviews/", response_model=List[ReviewResponse])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    sentiment: str = None,
    product_id: int = None,
    db: Session = Depends(get_db)
):
    """Récupérer les avis avec filtres optionnels"""
    query = db.query(Review)
    
    if sentiment:
        query = query.filter(Review.sentiment == sentiment)
    
    if product_id:
        query = query.filter(Review.product_id == product_id)
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews


@router.post("/analyze-sentiment/", response_model=SentimentAnalysisResponse)
def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyser le sentiment d'un texte"""
    try:
        # Prétraiter le texte
        processed_text, language = preprocessor.preprocess(request.text)
        
        # Détecter la langue si non fournie
        if request.language:
            language = request.language
        
        # Analyser le sentiment
        result = sentiment_analyzer.analyze(processed_text, language)
        
        return {
            "sentiment": result['sentiment'],
            "sentiment_score": result['sentiment_score'],
            "confidence": result['confidence'],
            "language_detected": language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")


@router.get("/products/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 50,
    category: str = None,
    min_sentiment: float = None,
    db: Session = Depends(get_db)
):
    """Récupérer les produits avec filtres"""
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    if min_sentiment is not None:
        query = query.filter(Product.sentiment_score >= min_sentiment)
    
    products = query.order_by(Product.sentiment_score.desc()).offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Récupérer un produit par ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product


@router.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Créer un nouveau produit"""
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du produit: {str(e)}")


@router.get("/recommendations/collaborative/{user_id}", response_model=List[RecommendationResponse])
def get_collaborative_recommendations(user_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    """Obtenir des recommandations par filtrage collaboratif"""
    try:
        recommendations = recommender.collaborative_filtering(db, user_id, top_n)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des recommandations: {str(e)}")


@router.get("/recommendations/content/{user_id}", response_model=List[RecommendationResponse])
def get_content_recommendations(user_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    """Obtenir des recommandations basées sur le contenu"""
    try:
        recommendations = recommender.content_based_filtering(db, user_id, top_n)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des recommandations: {str(e)}")


@router.get("/recommendations/hybrid/{user_id}", response_model=List[RecommendationResponse])
def get_hybrid_recommendations(user_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    """Obtenir des recommandations hybrides"""
    try:
        recommendations = recommender.hybrid_recommendation(db, user_id, top_n)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des recommandations: {str(e)}")


@router.get("/recommendations/trending/", response_model=List[RecommendationResponse])
def get_trending_products(category: str = None, top_n: int = 10, db: Session = Depends(get_db)):
    """Obtenir les produits tendance basés sur le sentiment"""
    try:
        recommendations = recommender.sentiment_weighted_recommendation(db, category, top_n)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des recommandations: {str(e)}")


@router.get("/stats/dashboard/")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obtenir les statistiques pour le dashboard"""
    try:
        total_reviews = db.query(Review).count()
        total_products = db.query(Product).count()
        
        positive_reviews = db.query(Review).filter(Review.sentiment == 'Positif').count()
        neutral_reviews = db.query(Review).filter(Review.sentiment == 'Neutre').count()
        negative_reviews = db.query(Review).filter(Review.sentiment == 'Négatif').count()
        
        # Note moyenne globale
        all_reviews = db.query(Review).all()
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 0
        
        # Sentiment moyen
        avg_sentiment = sum(r.sentiment_score for r in all_reviews) / len(all_reviews) if all_reviews else 0
        
        # CORRECTION : Utilisation correcte de func
        top_categories = db.query(
            Product.category,
            func.count(Product.id).label('count')
        ).group_by(Product.category).order_by(desc(func.count(Product.id))).limit(5).all()
        
        return {
            "total_reviews": total_reviews,
            "total_products": total_products,
            "positive_reviews": positive_reviews,
            "neutral_reviews": neutral_reviews,
            "negative_reviews": negative_reviews,
            "avg_rating": round(avg_rating, 2),
            "avg_sentiment": round(avg_sentiment, 2),
            "sentiment_distribution": {
                "positive_percentage": round((positive_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1),
                "neutral_percentage": round((neutral_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1),
                "negative_percentage": round((negative_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1)
            },
            "top_categories": [{"category": cat[0], "count": cat[1]} for cat in top_categories]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}")


# Endpoint de santé pour tester la connexion
@router.get("/health/")
def health_check():
    """Vérifier que l'API fonctionne"""
    return {
        "status": "healthy",
        "message": "FEELya API est opérationnelle!",
        "service": "sentiment_analysis"
    }


# Endpoint simple pour tester sans base de données
@router.get("/test/")
def test_endpoint():
    """Endpoint de test simple"""
    return {
        "message": "Backend FEELya fonctionne!",
        "endpoints_available": [
            "/health/",
            "/test/", 
            "/analyze-sentiment/",
            "/stats/dashboard/"
        ]
    }