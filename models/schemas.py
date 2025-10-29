from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ReviewBase(BaseModel):
    rating: float
    text: str
    language: Optional[str] = None

class ReviewCreate(ReviewBase):
    product_id: int
    user_id: Optional[int] = None

class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    confidence: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    price: float
    url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    avg_rating: float
    total_reviews: int
    sentiment_score: float
    positive_reviews: int
    neutral_reviews: int
    negative_reviews: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SentimentAnalysisRequest(BaseModel):
    text: str
    language: Optional[str] = None

class SentimentAnalysisResponse(BaseModel):
    sentiment: str
    sentiment_score: float
    confidence: float
    language_detected: str


class RecommendationResponse(BaseModel):
    product_id: int
    product_name: str
    score: float
    reason: str
    sentiment_score: float
    total_reviews: int
