import React, { useState, useEffect } from 'react';
import { 
  Database, Settings, Smile, ThumbsUp, BarChart3, Users, ShoppingCart, 
  Search, Star, TrendingUp, AlertCircle, CheckCircle, XCircle,
  RefreshCw, Download, Upload, Play, Activity, Zap, Globe
} from 'lucide-react';
import { apiService } from '../services/api';

export default function FEELyaApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [reviews, setReviews] = useState([]);
  const [filteredReviews, setFilteredReviews] = useState([]);
  const [products, setProducts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [isProcessing, setIsProcessing] = useState(false);
  const [stats, setStats] = useState({
    total_reviews: 0,
    positive_reviews: 0,
    neutral_reviews: 0,
    negative_reviews: 0,
    avg_rating: 0,
    sentiment_distribution: {
      positive_percentage: 0,
      neutral_percentage: 0,
      negative_percentage: 0
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charger les données au montage du composant
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Filtrer les avis selon la recherche et le sentiment
  useEffect(() => {
    let filtered = reviews;
    
    if (searchQuery) {
      filtered = filtered.filter(r => 
        r.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (r.product && r.product.name && r.product.name.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }
    
    if (sentimentFilter !== 'all') {
      filtered = filtered.filter(r => r.sentiment === sentimentFilter);
    }
    
    setFilteredReviews(filtered);
  }, [searchQuery, sentimentFilter, reviews]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Charger les statistiques
      const statsResponse = await apiService.getDashboardStats();
      setStats(statsResponse.data);
      
      // Charger les avis
      const reviewsResponse = await apiService.getReviews({ limit: 100 });
      setReviews(reviewsResponse.data);
      setFilteredReviews(reviewsResponse.data);
      
      // Charger les produits
      const productsResponse = await apiService.getProducts({ limit: 50 });
      setProducts(productsResponse.data);
      
      setLoading(false);
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      setError('Impossible de charger les données. Vérifiez que le backend est lancé.');
      setLoading(false);
    }
  };

  const processNewReview = async (reviewText) => {
    if (!reviewText.trim()) return;
    
    setIsProcessing(true);
    
    try {
      // Analyser le sentiment
      const sentimentResponse = await apiService.analyzeSentiment({ text: reviewText });
      
      // Afficher le résultat
      alert(`Sentiment détecté: ${sentimentResponse.data.sentiment}\nScore: ${sentimentResponse.data.sentiment_score.toFixed(2)}\nConfiance: ${(sentimentResponse.data.confidence * 100).toFixed(0)}%`);
      
      // Recharger les données
      await loadDashboardData();
    } catch (err) {
      console.error('Erreur lors de l\'analyse:', err);
      alert('Erreur lors de l\'analyse du sentiment');
    } finally {
      setIsProcessing(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'Positif': return 'text-green-600 bg-green-50 border-green-200';
      case 'Neutre': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Négatif': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'Positif': return <CheckCircle className="w-4 h-4" />;
      case 'Neutre': return <AlertCircle className="w-4 h-4" />;
      case 'Négatif': return <XCircle className="w-4 h-4" />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-800 mb-2 text-center">Erreur de connexion</h3>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold">
                F
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">FEELya</h1>
                <p className="text-sm text-gray-500">Système de Recommandation par Sentiment</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button 
                onClick={loadDashboardData}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
              >
                <RefreshCw className="w-4 h-4" />
                Actualiser
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 className="w-4 h-4" /> },
              { id: 'reviews', label: 'Avis Clients', icon: <Database className="w-4 h-4" /> },
              { id: 'analysis', label: 'Analyse', icon: <Activity className="w-4 h-4" /> },
              { id: 'recommendations', label: 'Recommandations', icon: <ThumbsUp className="w-4 h-4" /> }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-3 font-medium transition border-b-2 ${
                  activeTab === tab.id
                    ? 'text-purple-600 border-purple-600 bg-purple-50'
                    : 'text-gray-600 border-transparent hover:text-purple-600 hover:bg-gray-50'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Avis</p>
                    <p className="text-3xl font-bold text-gray-800">{stats.total_reviews}</p>
                  </div>
                  <Database className="w-10 h-10 text-purple-500" />
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Positifs</p>
                    <p className="text-3xl font-bold text-green-600">{stats.positive_reviews}</p>
                  </div>
                  <CheckCircle className="w-10 h-10 text-green-500" />
                </div>
                <p className="text-xs text-gray-500 mt-2">{stats.sentiment_distribution.positive_percentage}%</p>
              </div>
              
              <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-yellow-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Neutres</p>
                    <p className="text-3xl font-bold text-yellow-600">{stats.neutral_reviews}</p>
                  </div>
                  <AlertCircle className="w-10 h-10 text-yellow-500" />
                </div>
                <p className="text-xs text-gray-500 mt-2">{stats.sentiment_distribution.neutral_percentage}%</p>
              </div>
              
              <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Négatifs</p>
                    <p className="text-3xl font-bold text-red-600">{stats.negative_reviews}</p>
                  </div>
                  <XCircle className="w-10 h-10 text-red-500" />
                </div>
                <p className="text-xs text-gray-500 mt-2">{stats.sentiment_distribution.negative_percentage}%</p>
              </div>
              
              <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Note Moy.</p>
                    <p className="text-3xl font-bold text-blue-600">{stats.avg_rating}</p>
                  </div>
                  <Star className="w-10 h-10 text-blue-500 fill-blue-500" />
                </div>
                <p className="text-xs text-gray-500 mt-2">sur 5.0</p>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Distribution des Sentiments</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600">Positif</span>
                      <span className="font-semibold text-green-600">{stats.positive_reviews}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-green-500 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${stats.sentiment_distribution.positive_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600">Neutre</span>
                      <span className="font-semibold text-yellow-600">{stats.neutral_reviews}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-yellow-500 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${stats.sentiment_distribution.neutral_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-600">Négatif</span>
                      <span className="font-semibold text-red-600">{stats.negative_reviews}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-red-500 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${stats.sentiment_distribution.negative_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Activité Récente</h3>
                <div className="space-y-3">
                  {reviews.slice(0, 5).map((review, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className={`p-2 rounded-lg ${getSentimentColor(review.sentiment)}`}>
                        {getSentimentIcon(review.sentiment)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-800 truncate">
                          {review.text.substring(0, 50)}...
                        </p>
                        <p className="text-xs text-gray-500">{new Date(review.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        <span className="text-sm font-semibold">{review.rating}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Reviews Tab */}
        {activeTab === 'reviews' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Rechercher un avis..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>
                
                <div className="flex gap-2">
                  {['all', 'Positif', 'Neutre', 'Négatif'].map(filter => (
                    <button
                      key={filter}
                      onClick={() => setSentimentFilter(filter)}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        sentimentFilter === filter
                          ? 'bg-purple-500 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {filter === 'all' ? 'Tous' : filter}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Reviews List */}
            <div className="space-y-4">
              {filteredReviews.length === 0 ? (
                <div className="bg-white rounded-xl shadow-md p-12 text-center">
                  <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Aucun avis trouvé</p>
                </div>
              ) : (
                filteredReviews.map(review => (
                  <div key={review.id} className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${getSentimentColor(review.sentiment)}`}>
                            {getSentimentIcon(review.sentiment)}
                            {review.sentiment}
                          </span>
                          <span className="text-xs text-gray-500">{review.language.toUpperCase()}</span>
                        </div>
                        <p className="text-gray-600 mb-3">{review.text}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>{new Date(review.created_at).toLocaleDateString()}</span>
                          <span>•</span>
                          <span>Confiance: {(review.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 ml-4">
                        <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                        <span className="text-xl font-bold text-gray-800">{review.rating}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Zap className="w-6 h-6 text-purple-500" />
                Analyser un Nouvel Avis
              </h3>
              <textarea
                placeholder="Saisissez un avis client pour analyse de sentiment..."
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows="4"
                id="newReviewText"
              ></textarea>
              <button
                onClick={() => {
                  const text = document.getElementById('newReviewText').value;
                  if (text.trim()) {
                    processNewReview(text);
                    document.getElementById('newReviewText').value = '';
                  }
                }}
                disabled={isProcessing}
                className="mt-4 flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition disabled:opacity-50"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Analyser
                  </>
                )}
              </button>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl shadow-lg p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">Modèles NLP Utilisés</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <Globe className="w-8 h-8 mb-2" />
                  <h4 className="font-semibold mb-1">CamemBERT</h4>
                  <p className="text-sm opacity-90">Analyse du français</p>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <Globe className="w-8 h-8 mb-2" />
                  <h4 className="font-semibold mb-1">AraBERT</h4>
                  <p className="text-sm opacity-90">Analyse de l'arabe</p>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                  <Activity className="w-8 h-8 mb-2" />
                  <h4 className="font-semibold mb-1">Hybrid Model</h4>
                  <p className="text-sm opacity-90">Darija marocain</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recommendations Tab */}
        {activeTab === 'recommendations' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-purple-500" />
                Produits Recommandés (Basé sur le Sentiment)
              </h3>
              <div className="grid md:grid-cols-3 gap-6">
                {products.slice(0, 6).map((product, i) => (
                  <div key={i} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
                    <div className="bg-gray-100 rounded-lg h-40 flex items-center justify-center mb-4">
                      <ShoppingCart className="w-12 h-12 text-gray-400" />
                    </div>
                    <h4 className="font-bold text-gray-800 mb-2 truncate">{product.name}</h4>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        <span className="font-semibold">{product.avg_rating.toFixed(1)}</span>
                      </div>
                      <span className="text-sm text-green-600 font-semibold">
                        {product.total_reviews > 0 
                          ? Math.round((product.positive_reviews / product.total_reviews) * 100)
                          : 0}% Positif
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{product.total_reviews} avis</p>
                    <button className="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition">
                      Voir Détails
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Algorithme de Recommandation</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 font-bold">1</div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Filtrage Collaboratif</h4>
                    <p className="text-sm text-gray-600">Basé sur les préférences des utilisateurs similaires</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold">2</div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Analyse de Contenu</h4>
                    <p className="text-sm text-gray-600">Recommandations basées sur les caractéristiques des produits</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-bold">3</div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Pondération par Sentiment</h4>
                    <p className="text-sm text-gray-600">Priorisation des produits avec sentiments positifs</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
