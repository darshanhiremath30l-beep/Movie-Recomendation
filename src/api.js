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
    id: "tt12735488",
    title: "Kalki 2898 AD",
    genres: ["Sci-Fi", "Action"],
    rating: 7.6,
    year: 2024,
    duration: "3h 0m",
    synopsis: "When the world is consumed by darkness, a modern avatar descends to earth to protect the innocent from evil forces in a futuristic post-apocalyptic world.",
    poster: "https://m.media-amazon.com/images/M/MV5BZjJhMTFiN2UtMmQ4MC00MTZjLTk3NDYtYWRkNTFmNDQwNDFjXkEyXkFqcGc@._V1_SX300.jpg",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1200&auto=format&fit=crop",
    cast: ["Prabhas", "Amitabh Bachchan", "Kamal Haasan", "Deepika Padukone"],
    director: "Nag Ashwin"
  },
  {
    id: "tt15239678",
    title: "Dune: Part Two",
    genres: ["Sci-Fi", "Adventure"],
    rating: 8.5,
    year: 2024,
    duration: "2h 46m",
    synopsis: "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
    poster: "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGc@._V1_SX300.jpg",
    backdrop: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200&auto=format&fit=crop",
    cast: ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson"],
    director: "Denis Villeneuve"
  },
  {
    id: "tt28448834",
    title: "Stree 2",
    genres: ["Horror", "Comedy"],
    rating: 7.5,
    year: 2024,
    duration: "2h 27m",
    synopsis: "The town of Chanderi is haunted again by a headless entity named Sarkata. Vicky and his squad must save their town.",
    poster: "https://m.media-amazon.com/images/M/MV5BMjA4Y2E4NDEtN2VhNC00NWMxLWEyNWItN2JjY2ZlNDI3NzQ1XkEyXkFqcGc@._V1_SX300.jpg",
    backdrop: "https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?q=80&w=1200&auto=format&fit=crop",
    cast: ["Rajkummar Rao", "Shraddha Kapoor", "Pankaj Tripathi"],
    director: "Amar Kaushik"
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
