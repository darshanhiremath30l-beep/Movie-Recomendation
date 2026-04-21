const BASE_URL = 'http://127.0.0.1:5000/api';

export const interactWithMovie = async (movieId, action, payload = {}) => {
  try {
    const response = await fetch(`${BASE_URL}/interactions/${action}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: "default_user",
        movie_id: movieId,
        ...payload
      })
    });
    return await response.json();
  } catch (error) {
    console.error(`Error during ${action} interaction:`, error);
    return null;
  }
};

export const getRecommendations = async () => {
  try {
    const response = await fetch(`${BASE_URL}/recommendations/for-you?user_id=default_user`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return null;
  }
};

export const searchMovies = async (query) => {
  try {
    const res = await fetch(`${BASE_URL}/movies/search?q=${encodeURIComponent(query)}`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return { data: [] };
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
    console.error(err);
    return null;
  }
};
