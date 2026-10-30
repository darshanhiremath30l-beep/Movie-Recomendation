import { moviesData } from './data/mockData';

const BASE_URL = 'http://127.0.0.1:5000/api';

// Authentication API functions
export const loginUser = async (email, password) => {
  try {
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Login failed');
    }

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const registerUser = async (name, email, password) => {
  try {
    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed');
    }

    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

export const signupUser = async (email, name = '') => {
  try {
    const response = await fetch(`${BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, name })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Signup failed');
    }

    return data;
  } catch (error) {
    console.error('Signup error:', error);
    throw error;
  }
};

// Fallback movie data for when backend is unavailable
const fallbackMovies = moviesData;


export const interactWithMovie = async (movieId, action, payload = {}, userId = "default_user") => {
  try {
    const response = await fetch(`${BASE_URL}/interactions/${action}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        movie_id: movieId,
        ...payload
      })
    });
    return await response.json();
  } catch (error) {
    console.error(`Error during ${action} interaction:`, error);
    // Return success for offline mode
    return { success: true, message: "Action recorded (offline mode)" };
  }
};

export const getWatchlist = async (userId) => {
  try {
    if (!userId) return { data: [] };
    const response = await fetch(`${BASE_URL}/users/${userId}/watchlist`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching watchlist:", error);
    return { data: [] };
  }
};

export const getRecommendations = async (userId = "default_user") => {
  try {
    const response = await fetch(`${BASE_URL}/recommendations/for-you?user_id=${encodeURIComponent(userId)}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    // Return fallback recommendations
    return {
      data: fallbackMovies.slice(0, 3).map(movie => ({
        id: movie.id,
        title: movie.title,
        genres: movie.genres,
        synopsis: movie.synopsis,
        poster: movie.poster
      }))
    };
  }
};

export const matchMovieQuery = (movie, query) => {
  if (!query || !query.trim()) return true;
  const qClean = query.toLowerCase().trim();
  const terms = qClean.replace(/\b(movies?|films?|cinema)\b/g, '').trim().split(/\s+/).filter(Boolean);
  const targetTerms = terms.length > 0 ? terms : [qClean];

  const searchableText = [
    movie.title,
    movie.director,
    ...(movie.genres || []),
    ...(movie.cast || []),
    movie.synopsis
  ].filter(Boolean).join(' ').toLowerCase();

  return targetTerms.every(term => searchableText.includes(term)) || searchableText.includes(qClean);
};

export const searchMovies = async (query) => {
  try {
    const res = await fetch(`${BASE_URL}/movies/search?q=${encodeURIComponent(query)}`);
    return await res.json();
  } catch (err) {
    console.error("Search API error:", err);
    // Return filtered fallback movies based on query
    const filtered = fallbackMovies.filter(movie => matchMovieQuery(movie, query));
    return { data: filtered };
  }
};

export const getMovieDetailsAPI = async (id) => {
  try {
    const res = await fetch(`${BASE_URL}/movies/${id}`);
    const data = await res.json();
    if (data && data.data) {
      try {
        const resTrailer = await fetch(`${BASE_URL}/movies/${id}/trailer`);
        if (resTrailer.ok) {
          const trailerData = await resTrailer.json();
          data.data.trailerUrl = trailerData.trailer_url;
        }
      } catch (e) {
        // Trailer isn't strictly necessary to render page
      }
    }
    return data;
  } catch (err) {
    console.error("Movie details API error:", err);
    // Return fallback movie details
    const fallbackMovie = fallbackMovies.find(movie => movie.id === id);
    if (fallbackMovie) {
      return { data: fallbackMovie };
    }
    return null;
  }
};

export const fetchLiveMovies = async (limit = 12) => {
  try {
    const res = await fetch(`${BASE_URL}/movies/live?limit=${limit}`);
    if (res.ok) {
      const json = await res.json();
      return json.data || [];
    }
    return [];
  } catch (err) {
    console.error("Live movies API error:", err);
    return [];
  }
};

export const fetchMovieStreamingSources = async (movieId, region = 'IN') => {
  try {
    const res = await fetch(`${BASE_URL}/movies/${movieId}/sources?region=${region}`);
    if (res.ok) {
      const json = await res.json();
      return json.data || [];
    }
    return [];
  } catch (err) {
    console.error("Streaming sources API error:", err);
    return [];
  }
};
