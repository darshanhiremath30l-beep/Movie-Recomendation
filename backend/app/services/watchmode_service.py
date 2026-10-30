import os
import time
import requests

WATCHMODE_API_KEY = os.getenv('WATCHMODE_API_KEY', 'Gig7hnepzrfCgKpgp8Z2v2trDljGzh5T2OrYUl10').strip()
WATCHMODE_BASE_URL = 'https://api.watchmode.com/v1'

# Reusable HTTP session with connection pooling for maximum speed
_session = requests.Session()
_session.headers.update({
    'User-Agent': 'PopcornAI/1.0',
    'Accept': 'application/json'
})

# In-memory TTL cache: key -> (timestamp, data)
_cache = {}
CACHE_TTL = 600  # 10 minutes

def _get_cached(key):
    if key in _cache:
        cached_time, val = _cache[key]
        if time.time() - cached_time < CACHE_TTL:
            return val
    return None

def _set_cached(key, val):
    _cache[key] = (time.time(), val)

def _upgrade_poster_resolution(url):
    """Upgrade thumbnail TMDB URLs to high-resolution /w500/."""
    if not url:
        return 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=600&auto=format&fit=crop'
    return url.replace('/w185/', '/w500/').replace('/w92/', '/w500/')

def _upgrade_backdrop_resolution(url):
    """Upgrade thumbnail TMDB URLs to widescreen /w1280/."""
    if not url:
        return 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200&auto=format&fit=crop'
    return url.replace('/w185/', '/w1280/').replace('/w92/', '/w1280/').replace('/w500/', '/w1280/')

def get_live_releases(limit=16):
    """
    Fetch the latest live streaming movie & series releases across platforms
    (Netflix, Prime Video, Apple TV, Disney+ Hotstar, Paramount+, etc.).
    """
    cache_key = f"live_releases_{limit}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{WATCHMODE_BASE_URL}/releases/?apiKey={WATCHMODE_API_KEY}&limit={limit}"
        resp = _session.get(url, timeout=5.0)
        if resp.status_code != 200:
            return []

        data = resp.json()
        releases = data.get('releases', [])
        formatted = []
        seen_titles = set()
        for r in releases:
            title = r.get('title')
            if not title or title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())
            poster = _upgrade_poster_resolution(r.get('poster_url'))
            backdrop = _upgrade_backdrop_resolution(r.get('poster_url'))
            source_name = r.get('source_name', 'Live Streaming')
            rel_date = r.get('source_release_date', '')
            year = rel_date[:4] if rel_date else '2026'

            formatted.append({
                "id": r.get('imdb_id') or f"wm_{r.get('id')}",
                "watchmode_id": r.get('id'),
                "title": title,
                "year": year,
                "genres": ["Live Streaming", source_name],
                "rating": 7.5,
                "duration": "125m",
                "synopsis": f"Streaming premiere on {source_name} ({rel_date or 'Recently Added'}).",
                "poster": poster,
                "backdrop": backdrop,
                "source_name": source_name,
                "source_release_date": rel_date,
                "is_live": True,
                "trending": True,
                "newRelease": True
            })

        _set_cached(cache_key, formatted)
        return formatted
    except Exception as e:
        print(f"Notice: Watchmode get_live_releases error: {e}")
        return []

def search_watchmode_movies(query):
    """
    Search live movies across Watchmode's global streaming index.
    """
    if not query:
        return []
    clean_q = query.strip()
    cache_key = f"wm_search_{clean_q.lower()}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{WATCHMODE_BASE_URL}/autocomplete-search/?apiKey={WATCHMODE_API_KEY}&search_value={requests.utils.quote(clean_q)}&search_type=2"
        resp = _session.get(url, timeout=4.0)
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = data.get('results', [])
        formatted = []
        for item in results:
            title = item.get('name')
            if not title:
                continue
            poster = _upgrade_poster_resolution(item.get('image_url'))
            formatted.append({
                "id": item.get('imdb_id') or f"wm_{item.get('id')}",
                "watchmode_id": item.get('id'),
                "title": title,
                "year": str(item.get('year', '2024')),
                "genres": ["Live Stream", item.get('type', 'Movie').replace('_', ' ').title()],
                "rating": 7.2,
                "duration": "120m",
                "synopsis": f"{title} ({item.get('year', '2024')}) is available across global streaming networks.",
                "poster": poster,
                "backdrop": _upgrade_backdrop_resolution(item.get('image_url')),
                "is_live": True
            })

        _set_cached(cache_key, formatted)
        return formatted
    except Exception as e:
        print(f"Notice: Watchmode search error: {e}")
        return []

def get_streaming_sources(title_id_or_imdb_id, preferred_region="IN"):
    """
    Get live streaming providers (Netflix, Prime Video, Hotstar, Apple TV, etc.)
    with direct web URLs and availability for a given movie.
    Prioritizes Indian region (IN) then global providers.
    """
    if not title_id_or_imdb_id:
        return []
    clean_id = str(title_id_or_imdb_id).strip()
    cache_key = f"wm_sources_{clean_id}_{preferred_region}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        url = f"{WATCHMODE_BASE_URL}/title/{clean_id}/sources/?apiKey={WATCHMODE_API_KEY}"
        resp = _session.get(url, timeout=4.5)
        if resp.status_code != 200:
            return []

        sources = resp.json()
        if not isinstance(sources, list):
            return []

        # Prioritize matching region (e.g. IN for India)
        sorted_sources = sorted(
            sources,
            key=lambda s: 0 if s.get('region') == preferred_region else (1 if s.get('region') == 'US' else 2)
        )

        clean_list = []
        seen_providers = set()
        for s in sorted_sources:
            provider_name = s.get('name')
            stype = s.get('type')  # sub, rent, buy, free
            dedup_key = (provider_name, stype)
            if not provider_name or dedup_key in seen_providers:
                continue
            seen_providers.add(dedup_key)
            clean_list.append({
                "name": provider_name,
                "type": "Subscription" if stype == "sub" else ("Rent" if stype == "rent" else ("Buy" if stype == "buy" else "Free")),
                "region": s.get('region', 'Global'),
                "web_url": s.get('web_url'),
                "format": s.get('format', 'HD'),
                "price": s.get('price')
            })

        _set_cached(cache_key, clean_list)
        return clean_list
    except Exception as e:
        print(f"Notice: Watchmode streaming sources error: {e}")
        return []
