import { useContext } from 'react';
import { RecommendationContext } from '../RecommendationContext';
import MovieCard from '../components/MovieCard';

const Recommendations = () => {
  const { recommendations, isLoading } = useContext(RecommendationContext);

  return (
    <div className="page-container">
      <div className="section-title" style={{ marginBottom: '40px' }}>
        <div>
          <h2 style={{ background: 'linear-gradient(to right, #10b981, #3b82f6)', WebkitBackgroundClip: 'text', color: 'transparent' }}>Top Picks For You</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Dynamically adjusted by AI based on your interactions</p>
        </div>
      </div>

      {isLoading ? (
        <div style={{ color: 'var(--text-secondary)' }}>Analyzing your taste profile...</div>
      ) : recommendations && recommendations.length > 0 ? (
        <div className="movies-grid recommend-anim fade-in">
          {recommendations.map(movie => (
            <MovieCard key={`recpage-${movie.id}`} movie={movie} />
          ))}
        </div>
      ) : (
        <div style={{ color: 'var(--text-secondary)' }}>No recommendations yet. Go like some movies!</div>
      )}
    </div>
  );
};

export default Recommendations;
