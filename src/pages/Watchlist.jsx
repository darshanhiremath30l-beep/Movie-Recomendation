import { useEffect, useState, useContext } from 'react';
import { RecommendationContext } from '../RecommendationContext';
import { getWatchlist } from '../api';
import MovieCard from '../components/MovieCard';

const Watchlist = () => {
  const { user, isAuthenticated } = useContext(RecommendationContext);
  const [watchlistMovies, setWatchlistMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWatchlist = async () => {
      setLoading(true);
      if (isAuthenticated && user?._id) {
        const response = await getWatchlist(user._id);
        if (response && response.data) {
          setWatchlistMovies(response.data);
        }
      }
      setLoading(false);
    };

    fetchWatchlist();
  }, [user, isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '100px' }}>
        <h2>My Watchlist</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: '20px' }}>Log in to view your saved movies.</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="section-title">
        <h2>My Watchlist</h2>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <p>Loading your saved movies...</p>
        </div>
      ) : watchlistMovies.length > 0 ? (
        <div className="movies-grid">
          {watchlistMovies.map(movie => (
            <MovieCard key={`wl-${movie.id}`} movie={movie} />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <p>Your watchlist is empty.</p>
        </div>
      )}
    </div>
  );
};

export default Watchlist;
