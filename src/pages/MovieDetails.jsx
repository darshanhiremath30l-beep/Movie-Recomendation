import { useParams } from 'react-router-dom';
import { useContext, useState, useEffect } from 'react';
import { RecommendationContext } from '../RecommendationContext';
import { getMovieDetailsAPI } from '../api';
import { Star, Play, Plus, Heart, X, Video } from 'lucide-react';
import './MovieDetails.css';

const MovieDetails = () => {
  const { id } = useParams();
  const { interactWithMovie } = useContext(RecommendationContext);
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPlayer, setShowPlayer] = useState(false);
  const [showTrailer, setShowTrailer] = useState(false);
  
  // Anti-Ban Streaming Servers
  const servers = [
    { name: 'Server 1 (VidSrc CC)', url: `https://vidsrc.cc/v2/embed/movie/${id}` },
    { name: 'Server 2 (Embed.su)', url: `https://embed.su/embed/movie/${id}` },
    { name: 'Server 3 (VidLink)', url: `https://vidlink.pro/movie/${id}` },
    { name: 'Server 4 (Vidsrc Pro)', url: `https://vidsrc.pro/embed/movie/${id}` }
  ];
  const [activeServer, setActiveServer] = useState(servers[0].url);

  useEffect(() => {
    setLoading(true);
    getMovieDetailsAPI(id).then(res => {
      if (res && res.data) {
        setMovie(res.data);
      }
      setLoading(false);
    });
  }, [id]);

  if (loading) {
    return (
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <h2 className="text-gradient">Loading Movie Details...</h2>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <h2>Movie not found</h2>
      </div>
    );
  }

  return (
    <>
      <div className="details-page animate-fade-in">
        <div className="details-hero">
          <img src={movie.backdrop} alt={movie.title} className="details-backdrop" />
          <div className="details-overlay"></div>
        </div>

        <div className="page-container" style={{ paddingTop: 0 }}>
          <div className="details-content-wrapper">
            <img src={movie.poster} alt={movie.title} className="details-poster" />
            
            <div className="details-info">
              <h1 className="details-title">{movie.title}</h1>
              <div className="details-meta-row">
                <div className="rating" style={{ color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 'bold' }}>
                  <Star fill="currentColor" size={20} />
                  {movie.rating}
                </div>
                <span>|</span>
                <span>{movie.year}</span>
                <span>|</span>
                <span>{movie.duration}</span>
                <span>|</span>
                <span>{movie.genres.join(', ')}</span>
              </div>

              <div className="details-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={() => { interactWithMovie(movie.id, 'watch'); setShowPlayer(true); }}
                >
                  <Play size={20} fill="currentColor" />
                  Play Movie
                </button>
                {movie.trailerUrl && (
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => setShowTrailer(true)}
                    style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: '#ef4444', color: '#ef4444' }}
                  >
                    <Video size={20} />
                    Watch Trailer
                  </button>
                )}
                <button className="btn btn-secondary" onClick={() => interactWithMovie(movie.id, 'watchlist')}>
                  <Plus size={20} />
                  Add to Watchlist
                </button>
                <button className="btn btn-secondary" style={{ padding: '12px' }} onClick={() => interactWithMovie(movie.id, 'like')}>
                  <Heart size={20} />
                </button>
              </div>
            </div>
          </div>

          <div className="details-body">
            <div className="main-col">
              <div className="details-section">
                <h3>Storyline</h3>
                <p className="synopsis-text">{movie.synopsis}</p>
              </div>
              
              <div className="details-section">
                <h3>Cast</h3>
                <div className="cast-list">
                  {movie.cast && movie.cast.map((actor, idx) => (
                    <span key={idx} className="cast-item">{actor}</span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="side-col">
              <div className="details-section">
                <h3>Director</h3>
                <p className="synopsis-text">{movie.director}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Whole Movie Player Modal */}
      {showPlayer && (
        <div className="player-modal">
          <div className="player-modal-content" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="player-header" style={{ display: 'flex', gap: '10px', padding: '15px', background: '#0a0a0f', alignItems: 'center' }}>
               <h3 style={{ margin: 0, marginRight: '15px', fontSize: '16px' }}>Streaming Servers:</h3>
               {servers.map((s, idx) => (
                 <button 
                   key={idx} 
                   onClick={() => setActiveServer(s.url)}
                   style={{
                     padding: '6px 12px',
                     borderRadius: '4px',
                     background: activeServer === s.url ? '#10b981' : '#1b1b29',
                     color: '#fff',
                     border: activeServer === s.url ? '1px solid #10b981' : '1px solid #333',
                     cursor: 'pointer'
                   }}
                 >
                   {s.name}
                 </button>
               ))}
               <button onClick={() => setShowPlayer(false)} style={{ marginLeft: 'auto', background: 'transparent', color: '#ef4444', border: 'none', cursor: 'pointer' }}>
                 <X size={24} />
               </button>
            </div>
            <iframe 
              src={activeServer} 
              width="100%" 
              height="100%" 
              frameBorder="0" 
              allowFullScreen
              title="Movie Player"
              style={{ flex: 1 }}
            ></iframe>
          </div>
        </div>
      )}

      {/* Trailer Player Modal */}
      {showTrailer && movie.trailerUrl && (
        <div className="player-modal">
          <div className="player-modal-content">
            <button className="close-player-btn" onClick={() => setShowTrailer(false)}>
              <X size={24} />
            </button>
            <iframe 
              src={movie.trailerUrl} 
              width="100%" 
              height="100%" 
              frameBorder="0" 
              allowFullScreen
              title="Trailer Player"
            ></iframe>
          </div>
        </div>
      )}
    </>
  );
};

export default MovieDetails;
