// PopcornAI Movie Poster & Visual Fallback Utility

const genreThemes = {
  action: { bg1: '#241212', bg2: '#0b0c10', accent: '#ff4d4d', icon: '🔥' },
  'sci-fi': { bg1: '#071e2c', bg2: '#08090d', accent: '#00f0ff', icon: '🚀' },
  horror: { bg1: '#1e0c18', bg2: '#08090d', accent: '#a855f7', icon: '👻' },
  comedy: { bg1: '#24200c', bg2: '#08090d', accent: '#fbbf24', icon: '✨' },
  drama: { bg1: '#121422', bg2: '#08090d', accent: '#818cf8', icon: '🎭' },
  adventure: { bg1: '#0f221d', bg2: '#08090d', accent: '#10b981', icon: '🗺️' },
  romance: { bg1: '#260e1b', bg2: '#08090d', accent: '#ec4899', icon: '💖' },
  telugu: { bg1: '#261608', bg2: '#08090d', accent: '#f59e0b', icon: '🎬' },
  hindi: { bg1: '#210c1f', bg2: '#08090d', accent: '#ec4899', icon: '🍿' },
  default: { bg1: '#131524', bg2: '#08090d', accent: '#00f0ff', icon: '🍿' }
};

/**
 * Returns a sleek, self-contained SVG movie poster Data URI.
 * Guaranteed to display instantly with zero network requests or CORS issues.
 */
export const getFallbackPoster = (title = 'Movie', genres = [], year = '') => {
  const genresArr = Array.isArray(genres) ? genres : [genres || ''];
  const firstGenre = (genresArr[0] || '').toLowerCase();
  
  let theme = genreThemes.default;
  for (const [key, val] of Object.entries(genreThemes)) {
    if (firstGenre.includes(key)) {
      theme = val;
      break;
    }
  }

  const safeTitle = (title || 'Feature Film').replace(/[<>&"']/g, '');
  const safeGenres = genresArr.filter(Boolean).slice(0, 2).join(' • ') || 'PopcornAI Selection';
  const safeYear = year ? String(year) : '';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">
    <defs>
      <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${theme.bg1}"/>
        <stop offset="55%" stop-color="${theme.bg2}"/>
        <stop offset="100%" stop-color="#040507"/>
      </linearGradient>
      <radialGradient id="ambient" cx="50%" cy="30%" r="50%">
        <stop offset="0%" stop-color="${theme.accent}" stop-opacity="0.32"/>
        <stop offset="100%" stop-color="${theme.accent}" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${theme.accent}" stop-opacity="0.5"/>
        <stop offset="100%" stop-color="rgba(255,255,255,0.05)"/>
      </linearGradient>
    </defs>
    
    <!-- Poster Background -->
    <rect width="100%" height="100%" fill="url(#bgGrad)"/>
    <rect width="100%" height="100%" fill="url(#ambient)"/>
    
    <!-- Outer delicate border -->
    <rect x="12" y="12" width="376" height="576" rx="14" fill="none" stroke="url(#borderGrad)" stroke-width="1.5"/>

    <!-- Brand Badge -->
    <rect x="28" y="28" width="135" height="26" rx="13" fill="rgba(8, 8, 14, 0.7)" stroke="${theme.accent}" stroke-opacity="0.35"/>
    <text x="95" y="45" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" fill="${theme.accent}" letter-spacing="1.5" text-anchor="middle">🍿 POPCORNAI</text>

    <!-- Glowing Icon Emblem -->
    <circle cx="200" cy="210" r="52" fill="rgba(255,255,255,0.04)" stroke="${theme.accent}" stroke-opacity="0.4" stroke-width="1.5"/>
    <text x="200" y="225" font-size="40" text-anchor="middle">${theme.icon}</text>

    <!-- Movie Title -->
    <text x="200" y="330" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="22" font-weight="800" fill="#ffffff" text-anchor="middle" letter-spacing="0.5">${safeTitle.length > 22 ? safeTitle.slice(0, 20) + '...' : safeTitle}</text>
    
    <!-- Genres & Year -->
    <text x="200" y="365" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="600" fill="${theme.accent}" text-anchor="middle">${safeGenres}</text>
    ${safeYear ? `<text x="200" y="395" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#94a3b8" text-anchor="middle">${safeYear}</text>` : ''}

    <!-- Bottom Cinema Badge -->
    <line x1="50" y1="520" x2="350" y2="520" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
    <text x="200" y="548" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="10" fill="#64748b" letter-spacing="3" text-anchor="middle">PREMIUM STREAMING</text>
  </svg>`;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
};

/**
 * Validates and safely resolves an image URL, or returns fallback.
 */
export const resolvePoster = (movie) => {
  if (!movie) return getFallbackPoster();
  if (movie.poster && typeof movie.poster === 'string' && movie.poster.startsWith('http')) {
    return movie.poster;
  }
  return getFallbackPoster(movie.title, movie.genres, movie.year);
};

