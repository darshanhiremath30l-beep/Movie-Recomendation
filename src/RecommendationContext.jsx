import React, { createContext, useState, useEffect } from 'react';
import { getRecommendations, interactWithMovie as apiInteract, loginUser, registerUser, signupUser } from './api';
import Toast from './components/Toast';

export const RecommendationContext = createContext();

export const RecommendationProvider = ({ children }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [toast, setToast] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Authentication state
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);

  useEffect(() => {
    // Check if user is logged in (from localStorage)
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        localStorage.removeItem('user');
      }
    }

    fetchRecommendations();
  }, []);

  // Authentication functions
  const login = async (email, password) => {
    setAuthLoading(true);
    try {
      const response = await loginUser(email, password);
      const userData = response.user;

      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(userData));

      showToast('Login successful!', 'success');
      return { success: true };
    } catch (error) {
      showToast(error.message || 'Login failed', 'error');
      return { success: false, error: error.message };
    } finally {
      setAuthLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setAuthLoading(true);
    try {
      const response = await registerUser(name, email, password);
      const userData = response.user;

      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(userData));

      showToast('Registration successful!', 'success');
      return { success: true };
    } catch (error) {
      showToast(error.message || 'Registration failed', 'error');
      return { success: false, error: error.message };
    } finally {
      setAuthLoading(false);
    }
  };

  const signup = async (email, name = '') => {
    setAuthLoading(true);
    try {
      const response = await signupUser(email, name);
      const userData = response.user;

      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify(userData));

      showToast('Signup successful!', 'success');
      return { success: true };
    } catch (error) {
      showToast(error.message || 'Signup failed', 'error');
      return { success: false, error: error.message };
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
    showToast('Logged out successfully', 'info');
  };

  const fetchRecommendations = async () => {
    setIsLoading(true);
    try {
      const res = await getRecommendations();
      if (res && res.data) {
        setRecommendations(res.data);
      } else {
        // Fallback to mock data if API fails
        setRecommendations([
          {
            id: "m1",
            title: "Neon Skyline",
            genres: ["Sci-Fi", "Action"],
            synopsis: "In a neon-lit metropolis of the future, a rogue AI hunter must team up with an unlikely ally to prevent a city-wide blackout.",
            poster: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop"
          },
          {
            id: "m2",
            title: "Echoes of Silence",
            genres: ["Drama", "Mystery"],
            synopsis: "A small-time detective unravels a deep mystery in a quiet coastal town where nothing is as it seems.",
            poster: "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=600&auto=format&fit=crop"
          }
        ]);
      }
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      // Fallback to mock data
      setRecommendations([
        {
          id: "m1",
          title: "Neon Skyline",
          genres: ["Sci-Fi", "Action"],
          synopsis: "In a neon-lit metropolis of the future, a rogue AI hunter must team up with an unlikely ally to prevent a city-wide blackout.",
          poster: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop"
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const interactWithMovie = async (movieId, action, payload = {}) => {
    setIsLoading(true);
    const userId = user && user._id ? user._id : "default_user";
    const res = await apiInteract(movieId, action, payload, userId);
    
    // Update local user state if logged in
    if (user) {
      let updatedUser = { ...user };
      if (action === 'watchlist') {
        if (!updatedUser.watchlist) updatedUser.watchlist = [];
        if (!updatedUser.watchlist.includes(movieId)) {
          updatedUser.watchlist.push(movieId);
        }
      } else if (action === 'like') {
        if (!updatedUser.likes) updatedUser.likes = [];
        if (!updatedUser.likes.includes(movieId)) {
          updatedUser.likes.push(movieId);
        }
      }
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
    
    if (res && res.recommendations) {
      // Re-trigger animation by resetting first
      setRecommendations([]);
      setTimeout(() => setRecommendations(res.recommendations), 50);
      showToast(res.message);
    } else if (res && res.message) {
      showToast(res.message);
    }
    setIsLoading(false);
  };

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
  };

  return (
    <RecommendationContext.Provider value={{
      // Movie recommendations
      recommendations,
      interactWithMovie,
      isLoading,

      // Authentication
      user,
      isAuthenticated,
      authLoading,
      login,
      register,
      signup,
      logout
    }}>
      {children}
      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </RecommendationContext.Provider>
  );
};
