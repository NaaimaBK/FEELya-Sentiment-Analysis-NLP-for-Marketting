import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import random

class EcommerceScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': settings.SCRAPING_USER_AGENT
        }
        self.delay = settings.SCRAPING_DELAY
    
    def scrape_jumia_reviews(self, product_url: str) -> List[Dict]:
        """Scrape les avis depuis Jumia"""
        reviews = []
        try:
            # Ajouter un délai pour éviter d'être bloqué
            time.sleep(self.delay)
            
            response = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver les avis (adapter selon la structure HTML de Jumia)
            review_elements = soup.find_all('div', class_='review-item')
            
            for element in review_elements:
                try:
                    rating_elem = element.find('div', class_='rating')
                    text_elem = element.find('p', class_='review-text')
                    
                    if rating_elem and text_elem:
                        rating = float(rating_elem.get('data-rating', 0))
                        text = text_elem.text.strip()
                        
                        reviews.append({
                            'rating': rating,
                            'text': text,
                            'platform': 'jumia'
                        })
                except Exception as e:
                    print(f"Erreur lors du parsing d'un avis: {e}")
                    continue
            
        except Exception as e:
            print(f"Erreur lors du scraping: {e}")
        
        return reviews
    
    def scrape_product_info(self, product_url: str) -> Dict:
        """Scrape les informations d'un produit"""
        try:
            time.sleep(self.delay)
            response = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire les informations (adapter selon le site)
            name = soup.find('h1', class_='product-title')
            price = soup.find('span', class_='price')
            description = soup.find('div', class_='description')
            category = soup.find('span', class_='category')
            
            return {
                'name': name.text.strip() if name else '',
                'price': float(price.text.replace('DH', '').strip()) if price else 0.0,
                'description': description.text.strip() if description else '',
                'category': category.text.strip() if category else '',
                'url': product_url
            }
        except Exception as e:
            print(f"Erreur lors du scraping du produit: {e}")
            return {}
