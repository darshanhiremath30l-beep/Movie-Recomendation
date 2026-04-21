import { Link } from 'react-router-dom';
import { Film, Globe, MessageCircle, Mail, Camera } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-orb"></div>
      <div className="footer-content animate-fade-in">
        <div className="footer-brand">
          <Link to="/" className="footer-logo text-gradient">
            <Film className="icon" size={28} />
            CineMatch AI
          </Link>
          <p className="footer-desc">
            Your personal cinematic universe. Discover, track, and share the movies you love with our AI-powered recommendation engine.
          </p>
        </div>

        <div className="footer-column">
          <h4>Explore</h4>
          <div className="footer-links">
            <Link to="/">Home</Link>
            <Link to="/explore">Movies</Link>
            <Link to="/explore?genre=Action">Action</Link>
            <Link to="/explore?genre=Sci-Fi">Sci-Fi</Link>
          </div>
        </div>

        <div className="footer-column">
          <h4>Account</h4>
          <div className="footer-links">
            <Link to="/profile">My Profile</Link>
            <Link to="/watchlist">Watchlist</Link>
            <Link to="/recommendations">For You</Link>
            <Link to="/settings">Settings</Link>
          </div>
        </div>

        <div className="footer-column">
          <h4>App</h4>
          <div className="footer-links">
            <Link to="/about">About Us</Link>
            <Link to="/support">Support</Link>
            <Link to="/privacy">Privacy Policy</Link>
            <Link to="/terms">Terms of Service</Link>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} CineMatch AI. All rights reserved.</p>
        <div className="social-links">
          <a href="#" className="social-icon" aria-label="Twitter"><MessageCircle size={20} /></a>
          <a href="#" className="social-icon" aria-label="Instagram"><Camera size={20} /></a>
          <a href="#" className="social-icon" aria-label="Github"><Globe size={20} /></a>
          <a href="#" className="social-icon" aria-label="YouTube"><Mail size={20} /></a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
