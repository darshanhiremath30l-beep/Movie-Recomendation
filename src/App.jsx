import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Explore from './pages/Explore';
import MovieDetails from './pages/MovieDetails';
import Recommendations from './pages/Recommendations';
import Watchlist from './pages/Watchlist';
import Profile from './pages/Profile';
import Auth from './pages/Auth';
import './App.css';
import { RecommendationProvider } from './RecommendationContext';

function App() {
  return (
    <RecommendationProvider>
      <Router>
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/explore" element={<Explore />} />
              <Route path="/movie/:id" element={<MovieDetails />} />
              <Route path="/recommendations" element={<Recommendations />} />
              <Route path="/watchlist" element={<Watchlist />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/login" element={<Auth type="login" />} />
              <Route path="/signup" element={<Auth type="signup" />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </RecommendationProvider>
  );
}

export default App;
