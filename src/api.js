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
const fallbackMovies = [
  {
    id: "m1",
    title: "Neon Skyline",
    genres: ["Sci-Fi", "Action"],
    rating: 8.7,
    year: 2026,
    duration: "2h 14m",
    synopsis: "In a neon-lit metropolis of the future, a rogue AI hunter must team up with an unlikely ally to prevent a city-wide blackout.",
    poster: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1200&auto=format&fit=crop",
    cast: ["Elena R.", "Marcus T.", "Sam K."],
    director: "J. Cameron"
  },
  {
    id: "m2",
    title: "Echoes of Silence",
    genres: ["Drama", "Mystery"],
    rating: 7.9,
    year: 2025,
    duration: "1h 58m",
    synopsis: "A small-time detective unravels a deep mystery in a quiet coastal town where nothing is as it seems.",
    poster: "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?q=80&w=600&auto=format&fit=crop"
  },
  {
    id: "m3",
    title: "Midnight Protocol",
    genres: ["Thriller", "Action"],
    rating: 8.2,
    year: 2025,
    duration: "2h 5m",
    synopsis: "A cybersecurity expert races against time to prevent a global data breach that could expose every secret in the digital world.",
    poster: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=600&auto=format&fit=crop"
  }
];

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

export const getRecommendations = async () => {
  try {
    const response = await fetch(`${BASE_URL}/recommendations/for-you?user_id=default_user`);
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

export const searchMovies = async (query) => {
  try {
    const res = await fetch(`${BASE_URL}/movies/search?q=${encodeURIComponent(query)}`);
    return await res.json();
  } catch (err) {
    console.error("Search API error:", err);
    // Return filtered fallback movies based on query
    const filtered = fallbackMovies.filter(movie =>
      movie.title.toLowerCase().includes(query.toLowerCase()) ||
      movie.genres.some(genre => genre.toLowerCase().includes(query.toLowerCase()))
    );
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
