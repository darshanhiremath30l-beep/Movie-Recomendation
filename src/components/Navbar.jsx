import { useState, useEffect, useContext } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Search, Film, User, LogOut, LogIn } from 'lucide-react';
import { RecommendationContext } from '../RecommendationContext';
import './Navbar.css';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useContext(RecommendationContext);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/explore?search=${searchQuery}`);
      setSearchQuery('');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <Link to="/" className="nav-brand text-gradient">
        <Film className="icon" size={28} />
        CineMatch AI
      </Link>

      <div className="nav-links">
        <NavLink to="/" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>Home</NavLink>
        <NavLink to="/explore" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>Explore</NavLink>
        <NavLink to="/recommendations" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>For You</NavLink>
        <NavLink to="/watchlist" className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>Watchlist</NavLink>
      </div>

      <div className="nav-actions">
        <form onSubmit={handleSearch} className="search-container">
          <Search size={18} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search movies..."
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>

        {isAuthenticated ? (
          <div className="auth-actions">
            <Link to="/profile" className="profile-btn">
              <User size={20} />
              <span className="profile-name">{user?.name || 'User'}</span>
            </Link>
            <button onClick={handleLogout} className="logout-btn" title="Logout">
              <LogOut size={20} />
            </button>
          </div>
        ) : (
          <div className="auth-actions">
            <Link to="/login" className="login-btn">
              <LogIn size={20} />
              <span>Login</span>
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
