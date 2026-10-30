import { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Compass, LogIn } from 'lucide-react';
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
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div className="glass-panel" style={{ maxWidth: '480px', width: '100%', padding: '50px 30px', textAlign: 'center' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(0, 240, 255, 0.1)', border: '1px solid rgba(0, 240, 255, 0.3)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px', color: '#00f0ff' }}>
            <Bookmark size={30} />
          </div>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '10px' }}>Your Personal Watchlist</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '26px', lineHeight: 1.6 }}>Log in to view your saved movies and sync your recommendations with MongoDB.</p>
          <Link to="/login" className="btn btn-primary">
            <LogIn size={18} /> Log In Now
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="section-title">
        <h2>
          <Bookmark size={26} color="var(--accent-primary)" />
          My Watchlist
        </h2>
        {watchlistMovies.length > 0 && (
          <span className="smart-badge" style={{ fontSize: '12px', padding: '4px 12px', borderRadius: '20px' }}>
            {watchlistMovies.length} {watchlistMovies.length === 1 ? 'Movie' : 'Movies'}
          </span>
        )}
      </div>

      {loading ? (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
          <p>Syncing your saved movies from MongoDB Atlas...</p>
        </div>
      ) : watchlistMovies.length > 0 ? (
        <div className="movies-grid">
          {watchlistMovies.map(movie => (
            <MovieCard key={`wl-${movie.id}`} movie={movie} />
          ))}
        </div>
      ) : (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 30px', maxWidth: '500px', margin: '40px auto' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px', color: 'var(--text-muted)' }}>
            <Bookmark size={24} />
          </div>
          <h3 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Your Watchlist is Empty</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Save movies you want to watch later and train your AI recommendation engine.</p>
          <Link to="/explore" className="btn btn-primary">
            <Compass size={18} /> Discover Movies
          </Link>
        </div>
      )}
    </div>
  );
};

export default Watchlist;
