import React, { createContext, useState, useEffect } from 'react';
import { getRecommendations, interactWithMovie as apiInteract } from './api';
import Toast from './components/Toast';

export const RecommendationContext = createContext();

export const RecommendationProvider = ({ children }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [toast, setToast] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, []);

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
    }
    setIsLoading(false);
  };

  const interactWithMovie = async (movieId, action, payload = {}) => {
    setIsLoading(true);
    const res = await apiInteract(movieId, action, payload);
    if (res && res.recommendations) {
      // Re-trigger animation by resetting first
      setRecommendations([]); 
      setTimeout(() => setRecommendations(res.recommendations), 50);
      showToast(res.message);
    }
    setIsLoading(false);
  };

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
  };

  return (
    <RecommendationContext.Provider value={{ recommendations, interactWithMovie, isLoading }}>
      {children}
      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </RecommendationContext.Provider>
  );
};
