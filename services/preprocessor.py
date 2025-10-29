import re
import string
import unicodedata
from typing import Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Télécharger les ressources NLTK nécessaires
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class TextPreprocessor:
    def __init__(self):
        self.french_stopwords = set(stopwords.words('french'))
        self.arabic_stopwords = set(stopwords.words('arabic'))
        
        # Stopwords spécifiques au darija marocain
        self.darija_stopwords = {
            'واش', 'كيف', 'علاش', 'فين', 'شنو', 'منين', 'فوقاش',
            'بزاف', 'شوية', 'دابا', 'غدا', 'البارح', 'ديال'
        }
    
    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        # Compter les caractères arabes
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(re.findall(r'\w', text))
        
        if total_chars == 0:
            return 'unknown'
        
        arabic_ratio = arabic_chars / total_chars
        
        if arabic_ratio > 0.5:
            # Vérifier si c'est du darija (présence de mots spécifiques)
            if any(word in text for word in self.darija_stopwords):
                return 'darija'
            return 'ar'
        return 'fr'
    
    def clean_text(self, text: str, language: str = 'fr') -> str:
        """Nettoie le texte"""
        # Convertir en minuscules (seulement pour le français)
        if language == 'fr':
            text = text.lower()
        
        # Supprimer les URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Supprimer les emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Supprimer les mentions et hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Supprimer les emojis
        text = self.remove_emojis(text)
        
        # Supprimer les caractères spéciaux (garder les lettres arabes)
        if language in ['ar', 'darija']:
            text = re.sub(r'[^\u0600-\u06FF\s]', ' ', text)
        else:
            text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_emojis(self, text: str) -> str:
        """Supprime les emojis"""
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    
    def remove_stopwords(self, text: str, language: str = 'fr') -> str:
        """Supprime les stopwords"""
        words = word_tokenize(text)
        
        if language == 'fr':
            stopwords_set = self.french_stopwords
        elif language in ['ar', 'darija']:
            stopwords_set = self.arabic_stopwords.union(self.darija_stopwords)
        else:
            return text
        
        filtered_words = [word for word in words if word not in stopwords_set]
        return ' '.join(filtered_words)
    
    def preprocess(self, text: str) -> Tuple[str, str]:
        """Pipeline complet de prétraitement"""
        # Détection de la langue
        language = self.detect_language(text)
        
        # Nettoyage
        cleaned_text = self.clean_text(text, language)
        
        # Suppression des stopwords
        processed_text = self.remove_stopwords(cleaned_text, language)
        
        return processed_text, language

