import { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Compass, X } from 'lucide-react';
import { searchMovies, matchMovieQuery, fetchLiveMovies } from '../api';
import { moviesData } from '../data/mockData';
import MovieCard from '../components/MovieCard';
import './Explore.css';

const genresList = ['All', 'Live', 'Kannada', 'Telugu', 'Hindi', 'Tamil', 'Malayalam', 'Action', 'Sci-Fi', 'Comedy', 'Drama', 'Horror', 'Adventure'];

const Explore = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || '';
  const initialGenre = searchParams.get('genre') || 'All';
  
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [selectedGenre, setSelectedGenre] = useState(initialGenre);
  const [searchResults, setSearchResults] = useState([]);
  const [liveMovies, setLiveMovies] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLiveMovies(16).then(data => {
      if (data && data.length > 0) {
        setLiveMovies(data);
      }
    });
  }, []);

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
      }).catch(() => {
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

  const clearSearch = () => {
    searchParams.delete('search');
    setSearchParams(searchParams);
    setSearchQuery('');
    setSearchResults([]);
  };

  // Instant local catalog matches for zero-latency feedback
  const localMatches = useMemo(() => {
    if (!searchQuery) return [];
    return moviesData.filter(movie => matchMovieQuery(movie, searchQuery));
  }, [searchQuery]);

  // Combined and deduplicated movies to display
  const displayedMovies = useMemo(() => {
    if (searchQuery) {
      const seen = new Set();
      const combined = [];
      // Prioritize backend/API results merged with local catalog matches
      for (const m of [...searchResults, ...localMatches]) {
        if (!m) continue;
        const key = (m.title || m.id || '').trim().toLowerCase();
        if (key && !seen.has(key)) {
          seen.add(key);
          combined.push(m);
        }
      }
      return combined;
    }

    if (selectedGenre === 'All') {
      return moviesData;
    }

    if (selectedGenre === 'Live') {
      return liveMovies.length > 0 ? liveMovies : moviesData.filter(m => m.trending);
    }

    const gLower = selectedGenre.toLowerCase();
    return moviesData.filter(m => 
      m.genres && m.genres.some(g => g.toLowerCase().includes(gLower))
    );
  }, [searchQuery, searchResults, localMatches, selectedGenre]);

  return (
    <div className="page-container">
      <div className="section-title">
        <h2>
          <Compass size={28} color="var(--accent-primary)" />
          {searchQuery ? `Search Results for "${searchQuery}"` : 'Explore Catalog'}
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {searchQuery && (
            <button 
              onClick={clearSearch}
              className="smart-badge"
              style={{
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '12px',
                padding: '4px 12px',
                borderRadius: '20px',
                background: 'rgba(255, 77, 77, 0.15)',
                border: '1px solid rgba(255, 77, 77, 0.4)',
                color: '#ff6b6b'
              }}
            >
              Clear Search <X size={14} />
            </button>
          )}
          {displayedMovies.length > 0 && (
            <span className="smart-badge" style={{ fontSize: '12px', padding: '4px 12px', borderRadius: '20px' }}>
              {displayedMovies.length} Titles
            </span>
          )}
        </div>
      </div>

      <div className="explore-filters">
        {genresList.map(genre => (
          <button
            key={genre}
            className={`filter-chip ${selectedGenre === genre && !searchQuery ? 'active' : ''}`}
            onClick={() => handleGenreClick(genre)}
          >
            {genre}
          </button>
        ))}
      </div>

      {loading && displayedMovies.length === 0 ? (
        <div className="no-results glass-panel">
          <p>Searching global movie database...</p>
        </div>
      ) : displayedMovies.length > 0 ? (
        <div className="movies-grid">
          {displayedMovies.map(movie => (
            <MovieCard key={movie.id || movie.movie_id || movie.title} movie={movie} />
          ))}
        </div>
      ) : (
        <div className="no-results glass-panel">
          <p>No movies found matching "{searchQuery || selectedGenre}". Try searching for Kannada, Telugu, Hindi, Tamil, or actor names like Yash or Prabhas.</p>
        </div>
      )}
    </div>
  );
};

export default Explore;
