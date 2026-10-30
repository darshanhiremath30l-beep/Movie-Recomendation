import { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { Star, Plus, Heart, Check } from 'lucide-react';
import { RecommendationContext } from '../RecommendationContext';
import { getFallbackPoster } from '../utils/posterHelper';
import './MovieCard.css';

const MovieCard = ({ movie }) => {
  const [isLiked, setIsLiked] = useState(false);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [isAnimatingLike, setIsAnimatingLike] = useState(false);
  const [posterSrc, setPosterSrc] = useState(
    movie?.poster || getFallbackPoster(movie?.title, movie?.genres, movie?.year)
  );
  const { interactWithMovie } = useContext(RecommendationContext);

  useEffect(() => {
    setPosterSrc(movie?.poster || getFallbackPoster(movie?.title, movie?.genres, movie?.year));
  }, [movie?.poster, movie?.title, movie?.genres, movie?.year]);

  const handleImgError = () => {
    const fallback = getFallbackPoster(movie?.title, movie?.genres, movie?.year);
    if (posterSrc !== fallback) {
      setPosterSrc(fallback);
    }
  };

  const handleLike = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isLiked) {
      interactWithMovie(movie.id, 'like');
    }
    setIsLiked(!isLiked);
    setIsAnimatingLike(true);
    setTimeout(() => setIsAnimatingLike(false), 300);
  };

  const handleWatchlist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!inWatchlist) {
      interactWithMovie(movie.id, 'watchlist');
    }
    setInWatchlist(!inWatchlist);
  };

  return (
    <div className="movie-card animate-fade-in group" style={{ position: 'relative' }}>
      <Link to={`/movie/${movie.id}`} style={{ display: 'block', height: '100%', textDecoration: 'none', color: 'inherit' }}>
        <div className="movie-poster-wrapper" style={{ height: '100%', position: 'relative' }}>
          {movie.match_score && (
            <div style={{
              position: 'absolute',
              top: '10px',
              left: '10px',
              background: 'rgba(8, 8, 14, 0.78)',
              backdropFilter: 'blur(12px)',
              WebkitBackdropFilter: 'blur(12px)',
              border: '1px solid rgba(0, 240, 255, 0.45)',
              color: '#00f0ff',
              padding: '3px 9px',
              borderRadius: '20px',
              fontSize: '0.72rem',
              fontWeight: '700',
              letterSpacing: '0.4px',
              zIndex: 6,
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.8), 0 0 15px rgba(0, 240, 255, 0.35)'
            }}>
              ✨ {movie.match_score}
            </div>
          )}
          <img 
            src={posterSrc} 
            alt={movie.title} 
            className="movie-poster" 
            loading="lazy" 
            referrerPolicy="no-referrer"
            onError={handleImgError}
          />
          
          <div className="movie-overlay">
            {movie.ai_reason && (
              <div style={{ fontSize: '0.72rem', color: '#00f0ff', marginBottom: '4px', fontWeight: 600, textShadow: '0 0 10px rgba(0, 240, 255, 0.4)' }}>
                {movie.ai_reason}
              </div>
            )}
            <h3 className="movie-title">{movie.title}</h3>
            
            <div className="movie-meta">
              <div className="rating">
                <Star size={12} fill="#fbbf24" color="#fbbf24" />
                <span>{movie.rating}</span>
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{movie.year}</span>
            </div>
            
            <div className="genres">
              {movie.genres && movie.genres.slice(0, 2).map((genre, index) => (
                <span key={index} className="genre-tag">{genre}</span>
              ))}
            </div>
          </div>
        </div>
      </Link>

      <div className="card-actions" style={{ zIndex: 10 }}>
        <button 
          className={`action-btn ${isLiked ? 'active' : ''} ${isAnimatingLike ? 'pulse-anim' : ''}`} 
          onClick={handleLike}
          title={isLiked ? "Unlike" : "Like"}
        >
          <Heart size={16} fill={isLiked ? '#db2777' : 'transparent'} color={isLiked ? '#db2777' : 'currentColor'} strokeWidth={isLiked ? 0 : 2} />
        </button>
        <button 
          className={`action-btn ${inWatchlist ? 'active' : ''}`} 
          onClick={handleWatchlist}
          title={inWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
        >
          {inWatchlist ? <Check size={16} color="#10b981" /> : <Plus size={16} />}
        </button>
      </div>
    </div>
  );
};

export default MovieCard;
