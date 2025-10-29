from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from models.database import Base, engine

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FEELya API",
    description="Système de Recommandation par Sentiment pour E-commerce Marocain",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(router, prefix="/api/v1", tags=["FEELya"])


@app.get("/")
def root():
    return {
        "message": "Bienvenue sur FEELya API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
