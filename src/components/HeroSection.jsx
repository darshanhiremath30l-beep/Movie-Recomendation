import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Play, Info, Star } from 'lucide-react';
import './HeroSection.css';

const HeroSection = ({ movies }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!movies || movies.length === 0) return;
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % movies.length);
    }, 6000);
    return () => clearInterval(interval);
  }, [movies]);

  if (!movies || movies.length === 0) return null;

  return (
    <div className="hero-carousel-container">
      {movies.map((movie, index) => (
        <div 
          key={movie.id} 
          className={`hero-slide ${index === currentIndex ? 'active' : ''}`}
        >
          <img src={movie.backdrop} alt={movie.title} className="hero-backdrop" />
          <div className="hero-overlay"></div>
          
          <div className="hero-content">
            <h1 className="hero-title">{movie.title}</h1>
            
            <div className="hero-meta">
              <div className="hero-rating">
                <Star size={16} fill="currentColor" />
                {movie.rating}
              </div>
              <span className="dot-separator">•</span>
              <span>{movie.year}</span>
              <span className="dot-separator">•</span>
              <span>{movie.duration}</span>
              <span className="dot-separator">•</span>
              <span>{movie.genres.join(', ')}</span>
            </div>
            
            <p className="hero-synopsis">{movie.synopsis}</p>
            
            <div className="hero-actions">
              <button className="btn btn-primary">
                <Play size={20} fill="currentColor" />
                Watch Trailer
              </button>
              <Link to={`/movie/${movie.id}`} className="btn btn-secondary">
                <Info size={20} />
                More Info
              </Link>
            </div>
          </div>
        </div>
      ))}

      <div className="carousel-indicators">
        {movies.map((_, index) => (
          <button
            key={index}
            className={`indicator ${index === currentIndex ? 'active' : ''}`}
            onClick={() => setCurrentIndex(index)}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default HeroSection;
