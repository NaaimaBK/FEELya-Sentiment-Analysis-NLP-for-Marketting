import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict
from sqlalchemy.orm import Session
from models.database import Product, Review, User, UserPreference

class RecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.product_features = {}
    
    def collaborative_filtering(self, db: Session, user_id: int, top_n: int = 10) -> List[Dict]:
        """Filtrage collaboratif basé sur les utilisateurs similaires"""
        # Récupérer les avis de l'utilisateur
        user_reviews = db.query(Review).filter(Review.user_id == user_id).all()
        
        if not user_reviews:
            return []
        
        # Produits déjà notés par l'utilisateur
        rated_products = {r.product_id for r in user_reviews}
        
        # Trouver des utilisateurs similaires (qui ont noté les mêmes produits)
        similar_users = db.query(Review.user_id).filter(
            Review.product_id.in_(rated_products),
            Review.user_id != user_id
        ).distinct().all()
        
        # Recommandations basées sur ce que les utilisateurs similaires ont aimé
        recommendations = {}
        for similar_user in similar_users:
            user_id_sim = similar_user[0]
            reviews = db.query(Review).filter(
                Review.user_id == user_id_sim,
                Review.rating >= 4.0,
                ~Review.product_id.in_(rated_products)
            ).all()
            
            for review in reviews:
                if review.product_id not in recommendations:
                    recommendations[review.product_id] = {
                        'score': 0,
                        'count': 0
                    }
                recommendations[review.product_id]['score'] += review.rating
                recommendations[review.product_id]['count'] += 1
        
        # Calculer le score moyen
        for product_id in recommendations:
            recommendations[product_id]['score'] /= recommendations[product_id]['count']
        
        # Trier et retourner les top N
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:top_n]
        
        return self._format_recommendations(db, sorted_recommendations, 'collaborative')
    
    def content_based_filtering(self, db: Session, user_id: int, top_n: int = 10) -> List[Dict]:
        """Recommandation basée sur le contenu des produits"""
        # Récupérer les préférences de l'utilisateur
        user_prefs = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()
        
        if not user_prefs:
            return []
        
        # Catégories préférées
        preferred_categories = [pref.category for pref in user_prefs if pref.preference_score > 0]
        
        # Produits déjà vus/achetés
        user_reviews = db.query(Review).filter(Review.user_id == user_id).all()
        seen_products = {r.product_id for r in user_reviews}
        
        # Recommander des produits dans les catégories préférées
        recommendations = db.query(Product).filter(
            Product.category.in_(preferred_categories),
            ~Product.id.in_(seen_products),
            Product.sentiment_score > 0.3  # Seulement les produits bien notés
        ).order_by(
            Product.sentiment_score.desc(),
            Product.total_reviews.desc()
        ).limit(top_n).all()
        
        return [{
            'product_id': p.id,
            'product_name': p.name,
            'score': p.sentiment_score,
            'reason': f"Correspond à vos préférences ({p.category})",
            'sentiment_score': p.sentiment_score,
            'total_reviews': p.total_reviews
        } for p in recommendations]
    
    def hybrid_recommendation(self, db: Session, user_id: int, top_n: int = 10) -> List[Dict]:
        """Recommandation hybride combinant filtrage collaboratif et contenu"""
        # Obtenir les recommandations des deux méthodes
        collab_recs = self.collaborative_filtering(db, user_id, top_n * 2)
        content_recs = self.content_based_filtering(db, user_id, top_n * 2)
        
        # Combiner les scores
        combined_scores = {}
        
        # Poids pour chaque méthode
        collab_weight = 0.6
        content_weight = 0.4
        
        for rec in collab_recs:
            product_id = rec['product_id']
            combined_scores[product_id] = {
                'score': rec['score'] * collab_weight,
                'product': rec
            }
        
        for rec in content_recs:
            product_id = rec['product_id']
            if product_id in combined_scores:
                combined_scores[product_id]['score'] += rec['score'] * content_weight
            else:
                combined_scores[product_id] = {
                    'score': rec['score'] * content_weight,
                    'product': rec
                }
        
        # Trier et retourner les top N
        sorted_recs = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:top_n]
        
        results = []
        for product_id, data in sorted_recs:
            rec = data['product']
            rec['score'] = data['score']
            rec['reason'] = 'Recommandation personnalisée (hybride)'
            results.append(rec)
        
        return results
    
    def sentiment_weighted_recommendation(self, db: Session, category: str = None, top_n: int = 10) -> List[Dict]:
        """Recommandation pondérée par sentiment"""
        query = db.query(Product).filter(Product.total_reviews >= 5)
        
        if category:
            query = query.filter(Product.category == category)
        
        # Calculer un score composite
        products = query.all()
        scored_products = []
        
        for product in products:
            # Score basé sur: sentiment + nombre d'avis + note moyenne
            sentiment_weight = 0.5
            reviews_weight = 0.3
            rating_weight = 0.2
            
            # Normaliser le nombre d'avis (max 100)
            normalized_reviews = min(product.total_reviews / 100, 1.0)
            
            # Normaliser la note (0-5 vers 0-1)
            normalized_rating = product.avg_rating / 5.0
            
            # Score composite
            composite_score = (
                (product.sentiment_score + 1) / 2 * sentiment_weight +  # Convertir -1,1 en 0,1
                normalized_reviews * reviews_weight +
                normalized_rating * rating_weight
            )
            
            scored_products.append({
                'product_id': product.id,
                'product_name': product.name,
                'score': composite_score,
                'reason': f"{product.positive_reviews} avis positifs",
                'sentiment_score': product.sentiment_score,
                'total_reviews': product.total_reviews
            })
        
        # Trier et retourner les top N
        scored_products.sort(key=lambda x: x['score'], reverse=True)
        return scored_products[:top_n]
    
    def _format_recommendations(self, db: Session, recommendations: List, method: str) -> List[Dict]:
        """Formate les recommandations"""
        results = []
        for product_id, data in recommendations:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                results.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'score': data['score'],
                    'reason': f"Basé sur {method}",
                    'sentiment_score': product.sentiment_score,
                    'total_reviews': product.total_reviews
                })
        return results
