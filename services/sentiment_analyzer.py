import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Modèles pour différentes langues
        self.models = {}
        self.tokenizers = {}
        
        # Charger les modèles
        self._load_models()
    
    def _load_models(self):
        """Charge les modèles de sentiment"""
        try:
            # Modèle pour le français
            self.models['fr'] = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=self.device
            )
            
            # Modèle pour l'arabe (simulé - à remplacer par AraBERT)
            self.models['ar'] = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=self.device
            )
            
            # Pour le darija, on utilise une approche hybride
            self.models['darija'] = self.models['ar']
            
        except Exception as e:
            print(f"Erreur lors du chargement des modèles: {e}")
            # Fallback sur un modèle simple
            self.models['fr'] = None
            self.models['ar'] = None
            self.models['darija'] = None
    
    def analyze(self, text: str, language: str = 'fr') -> dict:
        """Analyse le sentiment d'un texte"""
        if not text or len(text.strip()) < 3:
            return {
                'sentiment': 'Neutre',
                'sentiment_score': 0.0,
                'confidence': 0.0
            }
        
        try:
            model = self.models.get(language, self.models['fr'])
            
            if model is None:
                # Analyse simple basée sur des mots-clés
                return self._simple_sentiment_analysis(text, language)
            
            # Analyse avec le modèle
            result = model(text[:512])[0]  # Limiter à 512 tokens
            
            # Convertir le label en sentiment
            sentiment, score = self._convert_label_to_sentiment(result['label'], result['score'])
            
            return {
                'sentiment': sentiment,
                'sentiment_score': score,
                'confidence': result['score']
            }
            
        except Exception as e:
            print(f"Erreur lors de l'analyse: {e}")
            return self._simple_sentiment_analysis(text, language)
    
    def _convert_label_to_sentiment(self, label: str, confidence: float) -> tuple[str, float]:
        """Convertit le label du modèle en sentiment"""
        # Pour le modèle nlptown (1-5 étoiles)
        if '5 stars' in label or '4 stars' in label:
            return 'Positif', 0.5 + (confidence * 0.5)
        elif '3 stars' in label:
            return 'Neutre', 0.0
        else:
            return 'Négatif', -0.5 - (confidence * 0.5)
    
    def _simple_sentiment_analysis(self, text: str, language: str) -> dict:
        """Analyse de sentiment simple basée sur des mots-clés"""
        positive_words_fr = {
            'excellent', 'super', 'génial', 'parfait', 'top', 'bien',
            'bon', 'qualité', 'satisfait', 'recommande', 'incroyable'
        }
        negative_words_fr = {
            'mauvais', 'nul', 'décevant', 'horrible', 'arnaque',
            'médiocre', 'cassé', 'défectueux', 'déçu'
        }
        
        positive_words_ar = {
            'ممتاز', 'رائع', 'جيد', 'جميل', 'أنصح', 'ممتازة'
        }
        negative_words_ar = {
            'سيء', 'سيئ', 'غير', 'راضي', 'خيبة'
        }
        
        text_lower = text.lower()
        
        if language == 'fr':
            pos_count = sum(1 for word in positive_words_fr if word in text_lower)
            neg_count = sum(1 for word in negative_words_fr if word in text_lower)
        else:
            pos_count = sum(1 for word in positive_words_ar if word in text)
            neg_count = sum(1 for word in negative_words_ar if word in text)
        
        if pos_count > neg_count:
            score = min(0.8, pos_count * 0.3)
            return {'sentiment': 'Positif', 'sentiment_score': score, 'confidence': 0.6}
        elif neg_count > pos_count:
            score = max(-0.8, -neg_count * 0.3)
            return {'sentiment': 'Négatif', 'sentiment_score': score, 'confidence': 0.6}
        else:
            return {'sentiment': 'Neutre', 'sentiment_score': 0.0, 'confidence': 0.5}

