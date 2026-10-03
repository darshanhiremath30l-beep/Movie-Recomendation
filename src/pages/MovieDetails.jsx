import { useParams } from 'react-router-dom';
import { useContext, useState, useEffect } from 'react';
import { RecommendationContext } from '../RecommendationContext';
import { getMovieDetailsAPI } from '../api';
import { Star, Play, Plus, Heart, X, ExternalLink, Video } from 'lucide-react';
import './MovieDetails.css';

// Mapping for mock dataset IDs to valid IMDb IDs for external streaming
const mockMovieImdbMap = {
  m1: 'tt1375666',
  m2: 'tt0111161',
  m3: 'tt0816692',
  m4: 'tt1630029',
  m5: 'tt0848228',
  m6: 'tt2582802',
  m7: 'tt1160419',
  m8: 'tt0468569',
};

// Verified YouTube trailer video IDs (guaranteed non-blocked)
const verifiedTrailers = {
  tt12735488: 'kPyZ5E7pTNE', // Kalki 2898 AD
  tt15239678: 'Way9Dexny3w', // Dune Part 2
  tt28448834: 'KVnheWAFiEU', // Stree 2
  tt6263850: '73_1biulkYk',  // Deadpool & Wolverine
  tt15398776: 'uYPbbksJxIg', // Oppenheimer
  tt15354916: 'COv52Qyctws', // Jawan
  tt8178634: 'Gy4Bgd332T0',  // RRR
  tt10698680: 'JKa05nyUjQg', // K.G.F Chapter 2
  m1: 'YoHD9XEInc0',
  m2: 'PLl99DfY644',
  m3: 'zSWdZVtXT7E',
  m4: 'd9MyW72ELq0',
  m5: 'EXeTwQWrcwY'
};

const MovieDetails = () => {
  const { id } = useParams();
  const { interactWithMovie } = useContext(RecommendationContext);
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPlayer, setShowPlayer] = useState(false);
  const [useTrailer, setUseTrailer] = useState(false);

  useEffect(() => {
    setLoading(true);
    setUseTrailer(false);
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

  // Resolved target IMDb ID for full feature stream
  const targetImdbId = id && id.startsWith('tt') ? id : (mockMovieImdbMap[id] || 'tt15239678');
  const fullStreamUrl = `https://www.2embed.cc/embed/${targetImdbId}`;

  // Trailer Embed URL
  const trailerEmbedUrl = verifiedTrailers[id] 
    ? `https://www.youtube-nocookie.com/embed/${verifiedTrailers[id]}?autoplay=1`
    : `https://www.youtube-nocookie.com/embed/Way9Dexny3w?autoplay=1`;

  const activeVideoUrl = useTrailer ? trailerEmbedUrl : fullStreamUrl;

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
                <span>{Array.isArray(movie.genres) ? movie.genres.join(', ') : movie.genres}</span>
              </div>

              <div className="details-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={() => { interactWithMovie(movie.id, 'watch'); setUseTrailer(false); setShowPlayer(true); }}
                >
                  <Play size={20} fill="currentColor" />
                  Play Movie
                </button>

                <button 
                  className="btn btn-secondary" 
                  onClick={() => { interactWithMovie(movie.id, 'watch'); setUseTrailer(true); setShowPlayer(true); }}
                >
                  <Video size={20} />
                  Watch Trailer
                </button>
                
                <button 
                  className="btn btn-secondary" 
                  onClick={() => window.open(fullStreamUrl, '_blank')}
                  title="Open Full Screen Stream in New Tab"
                >
                  <ExternalLink size={20} />
                  Full Stream
                </button>

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

      {/* Video Player Modal */}
      {showPlayer && (
        <div className="player-modal">
          <div className="player-modal-content" style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 16px', background: '#0a0a0f', borderBottom: '1px solid #1f1f2e' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  onClick={() => setUseTrailer(false)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    background: !useTrailer ? '#10b981' : '#1b1b29',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: '600'
                  }}
                >
                  Movie Stream
                </button>
                <button 
                  onClick={() => setUseTrailer(true)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    background: useTrailer ? '#3b82f6' : '#1b1b29',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: '600'
                  }}
                >
                  HD Trailer
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <button 
                  onClick={() => window.open(fullStreamUrl, '_blank')}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
                >
                  <ExternalLink size={14} /> Open Stream Mirror
                </button>
                <button onClick={() => setShowPlayer(false)} style={{ background: 'transparent', color: '#ef4444', border: 'none', cursor: 'pointer' }}>
                  <X size={24} />
                </button>
              </div>
            </div>

            <div style={{ flex: 1, position: 'relative', background: '#000' }}>
              <iframe 
                src={activeVideoUrl} 
                width="100%" 
                height="100%" 
                frameBorder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title="Movie Player"
                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
              ></iframe>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MovieDetails;




