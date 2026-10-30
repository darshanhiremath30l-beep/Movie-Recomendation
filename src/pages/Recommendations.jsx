import { useContext } from 'react';
import { Sparkles, Compass } from 'lucide-react';
import { Link } from 'react-router-dom';
import { RecommendationContext } from '../RecommendationContext';
import MovieCard from '../components/MovieCard';

const Recommendations = () => {
  const { recommendations, isLoading } = useContext(RecommendationContext);

  return (
    <div className="page-container">
      <div className="section-title" style={{ marginBottom: '36px', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <h2 style={{ 
              background: 'linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%)', 
              WebkitBackgroundClip: 'text', 
              WebkitTextFillColor: 'transparent',
              fontSize: '2.4rem',
              fontWeight: 800
            }}>
              AI Picks For You
            </h2>
            <span className="smart-badge" style={{ fontSize: '12px', padding: '4px 12px', borderRadius: '20px' }}>
              ✨ Live Vectors
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem' }}>
            Personalized in real-time from your likes, watchlist, and watch history on MongoDB Atlas
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '70px 20px', color: 'var(--text-secondary)' }}>
          <div style={{ fontSize: '1.2rem', color: '#00f0ff', marginBottom: '8px' }}>✨ Computing Cosine Vectors...</div>
          <p>Analyzing your multi-table preference signals</p>
        </div>
      ) : recommendations && recommendations.length > 0 ? (
        <div className="movies-grid recommend-anim fade-in">
          {recommendations.map(movie => (
            <MovieCard key={`recpage-${movie.id}`} movie={movie} />
          ))}
        </div>
      ) : (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 30px', maxWidth: '500px', margin: '40px auto' }}>
          <Sparkles size={36} color="#00f0ff" style={{ marginBottom: '16px' }} />
          <h3 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>No Preferences Found Yet</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Like or watch a movie to teach your AI algorithm what stories you love.
          </p>
          <Link to="/explore" className="btn btn-primary">
            <Compass size={18} /> Explore Catalog
          </Link>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
