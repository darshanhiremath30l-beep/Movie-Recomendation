import { moviesData, userData } from '../data/mockData';
import MovieCard from '../components/MovieCard';

const Watchlist = () => {
  const watchlistMovies = moviesData.filter(movie => userData.watchlist.includes(movie.id));

  return (
    <div className="page-container">
      <div className="section-title">
        <h2>My Watchlist</h2>
      </div>

      {watchlistMovies.length > 0 ? (
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
