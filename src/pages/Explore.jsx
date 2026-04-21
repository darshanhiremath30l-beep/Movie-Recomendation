import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchMovies } from '../api';
import MovieCard from '../components/MovieCard';
import './Explore.css';

const Explore = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || '';
  
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [filteredMovies, setFilteredMovies] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const q = searchParams.get('search') || '';
    setSearchQuery(q);
    
    if (q) {
      setLoading(true);
      searchMovies(q).then(res => {
        setFilteredMovies(res.data || []);
        setLoading(false);
      });
    } else {
      setFilteredMovies([]);
    }
  }, [searchParams]);

  return (
    <div className="page-container">
      <div className="section-title">
        <h2>{searchQuery ? `Search Results for "${searchQuery}"` : 'Explore Movies'}</h2>
      </div>

      {!searchQuery && (
        <div className="no-results" style={{ padding: '40px', background: 'var(--glass-bg)', borderRadius: '12px' }}>
           <p>Type a movie name in the top search bar to find real-time results from OMDB!</p>
        </div>
      )}

      {loading ? (
        <div className="no-results" style={{ padding: '40px' }}><p>Searching global database...</p></div>
      ) : filteredMovies.length > 0 ? (
        <div className="movies-grid">
          {filteredMovies.map(movie => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      ) : searchQuery && !loading ? (
        <div className="no-results" style={{ padding: '40px' }}>
          <p>No movies found matching "{searchQuery}".</p>
        </div>
      ) : null}
    </div>
  );
};

export default Explore;
