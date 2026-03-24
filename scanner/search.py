import re
import logging
import requests
from typing import List, Dict

from ..config import settings
from ..core.utils import match_str
from ..importer.metadata import get_event_name_from_torrent

logger = logging.getLogger(__name__)

FULL_EVENT_PATTERN = re.compile(r"(^|[\W_])(full(\.event)?|complete|all\.fights?)($|[\W_])", re.IGNORECASE)
PRELIMS_PATTERN = re.compile(r"(^|[\W_])(prelims?|early\.prelims?|undercard)($|[\W_])", re.IGNORECASE)
MAIN_CARD_PATTERN = re.compile(r"(^|[\W_])(main\.card|maincard|main\.event)($|[\W_])", re.IGNORECASE)

resolution = str(settings.quality_preference) if settings.quality_preference else "1080"
language = str(settings.language_preference) if settings.language_preference else "en"
codec = str(settings.codec_preference) if settings.codec_preference else "x265"

# Language synonyms mapping
LANG_MAP = {
    "en": "en|eng|english",
    "ru": "ru|rus|russian",
    "it": "it|ita|italian",
    "fr": "fr|french",
    "es": "es|esp|spanish",
    "de": "de|german",
    "pl": "pl|polish",
    "nl": "nl|dutch",
}

# Codec synonyms mapping
CODEC_MAP = {
    "x264": "x264|h\\.?264|avc",
    "h264": "x264|h\\.?264|avc",
    "x265": "x265|h\\.?265|hevc",
    "h265": "x265|h\\.?265|hevc",
}

# Dynamic patterns based on settings
language = LANG_MAP.get(language, language)
codec = CODEC_MAP.get(codec, codec)

QUAL_PATTERN = re.compile(r"(^|[\W_])" + resolution + r"p?($|[\W_])", re.IGNORECASE)
LANG_PATTERN = re.compile(r"(^|[\W_])(" + language + r")($|[\W_])", re.IGNORECASE)
CODEC_PATTERN = re.compile(r"(^|[\W_])(" + codec + r")($|[\W_])", re.IGNORECASE)

def search_prowlarr(query: str) -> List[Dict]:
    if not settings.prowlarr_api_key:
        logger.error("Prowlarr API key missing")
        return []

    url = f"{settings.prowlarr_url.rstrip('/')}/api/v1/search"
    params = {
        "query": query,
        "type": "search",
        "categories": [5060],  # TV/Sport
        "limit": 100,
    }
    headers = {"X-Api-Key": settings.prowlarr_api_key}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Prowlarr search error for {query}: {e}")
        return []

def classify_card_kind(title: str) -> str:
    if FULL_EVENT_PATTERN.search(title): return "full"
    if PRELIMS_PATTERN.search(title): return "prelims"
    if MAIN_CARD_PATTERN.search(title): return "main"
    return "other"

def release_sort_key(item: Dict) -> tuple:
    title = str(item.get("title") or "")
    seeders = item.get("seeders", 0)
    size = item.get("size", 0)

    # Preferences from settings
    is_pref_lang = 0 if LANG_PATTERN.search(title) else 1
    is_pref_quality = 0 if QUAL_PATTERN.search(title) else 1
    is_pref_codec = 0 if CODEC_PATTERN.search(title) else 1
    
    return (is_pref_lang, is_pref_quality, is_pref_codec, -int(seeders), -int(size))

def find_best_releases(event_name: str) -> List[Dict]:
    results = search_prowlarr(event_name)
    candidates = []
    for item in results:
        if get_event_name_from_torrent(item.get("title", "")) == event_name:
            candidates.append(item)
    
    if not candidates:
        return []

    # Organize candidates
    full_events = [c for c in candidates if classify_card_kind(c['title']) == "full"]
    main_cards = [c for c in candidates if classify_card_kind(c['title']) == "main"]
    prelims = [c for c in candidates if classify_card_kind(c['title']) == "prelims"]

    preferred_mode = settings.full_or_main
    
    if preferred_mode == "main_only":
        if main_cards:
            main_cards.sort(key=release_sort_key)
            return [main_cards[0]]
        if full_events:
            full_events.sort(key=release_sort_key)
            return [full_events[0]]

    else:
        if full_events:
            full_events.sort(key=release_sort_key)
            return [full_events[0]]
        if prelims and main_cards:
            prelims.sort(key=release_sort_key)
            main_cards.sort(key=release_sort_key)
            return [prelims[0], main_cards[0]]

    candidates.sort(key=release_sort_key)
    return [candidates[0]]
