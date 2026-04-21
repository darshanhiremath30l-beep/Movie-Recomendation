import { useContext } from 'react';
import { RecommendationContext } from '../RecommendationContext';
import { moviesData } from '../data/mockData';
import { useIntersectionObserver } from '../hooks/useIntersectionObserver';
import HeroSection from '../components/HeroSection';
import MovieCard from '../components/MovieCard';
import { ChevronRight, Sparkles } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import './Home.css';

// Reusable animated section component
const AnimatedSection = ({ children, className = '' }) => {
  const [ref, isVisible] = useIntersectionObserver();
  return (
    <section ref={ref} className={`fade-in-section ${isVisible ? 'is-visible' : ''} ${className}`}>
      {children}
    </section>
  );
};

const topGenres = [
  { name: 'Action', image: 'https://images.unsplash.com/photo-1542204165-65bf26472b9b?q=80&w=600&auto=format&fit=crop' },
  { name: 'Sci-Fi', image: 'https://images.unsplash.com/photo-1620336655055-088d06e36bf0?q=80&w=600&auto=format&fit=crop' },
  { name: 'Horror', image: 'https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=600&auto=format&fit=crop' },
  { name: 'Romance', image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=600&auto=format&fit=crop' }
];

const Home = () => {
  const navigate = useNavigate();
  const { recommendations, isLoading } = useContext(RecommendationContext);

  // For the cinematic hero, we take top 3 trending movies
  const cinematicMovies = moviesData.filter(m => m.trending).slice(0, 3);
  
  // Other rows
  const trendingMovies = moviesData.slice(0, 4);
  const newReleases = moviesData.slice(4, 8);

  return (
    <div className="home-page">
      <HeroSection movies={cinematicMovies} />
      
      <div className="page-container" style={{ paddingTop: '60px' }}>
        
        <AnimatedSection className="mb-12">
          <div className="section-title">
            <h2>Trending Now</h2>
            <Link to="/explore" className="view-all">
              Explore All <ChevronRight size={18} />
            </Link>
          </div>
          <div className="movies-grid">
            {trendingMovies.map(movie => (
              <MovieCard key={movie.id} movie={movie} />
            ))}
          </div>
        </AnimatedSection>

        {recommendations && recommendations.length > 0 && (
          <AnimatedSection className="mb-12" style={{ marginTop: '80px' }}>
            <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <h2 style={{ background: 'linear-gradient(to right, #10b981, #3b82f6)', WebkitBackgroundClip: 'text', color: 'transparent' }}>Recommended for You</h2>
              <span className="smart-badge" style={{ fontSize: '12px', background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', padding: '4px 10px', borderRadius: '20px' }}>Real-time Suggestion</span>
            </div>
            {isLoading ? (
              <div style={{ color: 'var(--text-secondary)' }}>Analyzing preferences...</div>
            ) : (
              <div className="movies-grid recommend-anim fade-in">
                {recommendations.slice(0, 4).map(movie => (
                  <MovieCard key={`rec-${movie.id}`} movie={movie} />
                ))}
              </div>
            )}
          </AnimatedSection>
        )}

        <AnimatedSection className="mb-12" style={{ marginTop: '80px' }}>
          <div className="section-title">
            <h2>Top Genres</h2>
          </div>
          <div className="genres-grid">
            {topGenres.map((genre, idx) => (
              <Link to={`/explore?genre=${genre.name}`} key={idx} className="genre-card" style={{ backgroundImage: `url(${genre.image})` }}>
                <h3>{genre.name}</h3>
              </Link>
            ))}
          </div>
        </AnimatedSection>

        <AnimatedSection className="mb-12" style={{ marginTop: '80px' }}>
          <div className="section-title">
            <h2>New Releases</h2>
            <Link to="/explore" className="view-all">
              See More <ChevronRight size={18} />
            </Link>
          </div>
          <div className="movies-grid">
            {newReleases.map((movie) => (
              <MovieCard key={`new-${movie.id}`} movie={movie} />
            ))}
          </div>
        </AnimatedSection>

        <AnimatedSection className="cta-section">
          <div className="cta-content">
            <h2 className="cta-title">Not Sure What To Watch?</h2>
            <p className="cta-desc">Let our AI analyze your taste and build a personalized pipeline of movies tailored perfectly for you.</p>
            <button className="btn btn-primary" onClick={() => navigate('/recommendations')}>
              <Sparkles size={20} />
              Get Recommendations
            </button>
          </div>
        </AnimatedSection>

      </div>
    </div>
  );
};

export default Home;
