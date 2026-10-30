import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Compass } from 'lucide-react';
import { searchMovies } from '../api';
import { moviesData } from '../data/mockData';
import MovieCard from '../components/MovieCard';
import './Explore.css';

const genresList = ['All', 'Action', 'Sci-Fi', 'Comedy', 'Drama', 'Horror', 'Adventure'];

const Explore = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || '';
  const initialGenre = searchParams.get('genre') || 'All';
  
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [selectedGenre, setSelectedGenre] = useState(initialGenre);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const q = searchParams.get('search') || '';
    const g = searchParams.get('genre') || 'All';
    setSearchQuery(q);
    setSelectedGenre(g);
    
    if (q) {
      setLoading(true);
      searchMovies(q).then(res => {
        setSearchResults(res.data || []);
        setLoading(false);
      });
    } else {
      setSearchResults([]);
    }
  }, [searchParams]);

  const handleGenreClick = (genre) => {
    setSelectedGenre(genre);
    if (genre === 'All') {
      searchParams.delete('genre');
    } else {
      searchParams.set('genre', genre);
    }
    setSearchParams(searchParams);
  };

  // Determine movies to display
  let displayedMovies = [];
  if (searchQuery) {
    displayedMovies = searchResults;
  } else {
    displayedMovies = selectedGenre === 'All' 
      ? moviesData 
      : moviesData.filter(m => m.genres && m.genres.some(g => g.toLowerCase().includes(selectedGenre.toLowerCase())));
  }

  return (
    <div className="page-container">
      <div className="section-title">
        <h2>
          <Compass size={28} color="var(--accent-primary)" />
          {searchQuery ? `Search Results for "${searchQuery}"` : 'Explore Catalog'}
        </h2>
        {displayedMovies.length > 0 && (
          <span className="smart-badge" style={{ fontSize: '12px', padding: '4px 12px', borderRadius: '20px' }}>
            {displayedMovies.length} Titles
          </span>
        )}
      </div>

      {!searchQuery && (
        <div className="explore-filters">
          {genresList.map(genre => (
            <button
              key={genre}
              className={`filter-chip ${selectedGenre === genre ? 'active' : ''}`}
              onClick={() => handleGenreClick(genre)}
            >
              {genre}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <div className="no-results glass-panel">
          <p>Searching global movie database...</p>
        </div>
      ) : displayedMovies.length > 0 ? (
        <div className="movies-grid">
          {displayedMovies.map(movie => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      ) : (
        <div className="no-results glass-panel">
          <p>No movies found matching your criteria.</p>
        </div>
      )}
    </div>
  );
};

export default Explore;
