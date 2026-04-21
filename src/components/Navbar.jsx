import { useState, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Search, Film, User, LogOut } from 'lucide-react';
import { userData } from '../data/mockData';
import './Navbar.css';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

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
        
        <Link to="/profile" className="profile-btn">
          <img src={userData.avatar} alt="Profile" className="avatar" />
          <span className="profile-name">Alex</span>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
