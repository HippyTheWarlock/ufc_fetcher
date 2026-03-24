import logging
import requests
from datetime import datetime
from typing import List, Dict

from ufc_fetcher.config import settings
from ufc_fetcher.importer.metadata import get_event_name_from_torrent

logger = logging.getLogger(__name__)

def get_next_league_events() -> List[Dict]:
    url = f"{settings.sports_db_url}/eventsnextleague.php?id=4443"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json().get("events") or []
    except Exception as e:
        logger.error(f"Error fetching next events: {e}")
        return []

def get_recent_league_events() -> List[Dict]:
    url = f"{settings.sports_db_url}/eventspastleague.php?id=4443"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json().get("events") or []
    except Exception as e:
        logger.error(f"Error fetching past events: {e}")
        return []

def collect_relevant_events() -> List[Dict]:
    """Combine, filter, and deduplicate upcoming events."""
    seen_ids = set()
    combined = []
    today = datetime.now().date()
    
    # Simple collection for the refactored version
    sources = get_next_league_events() + get_recent_league_events()
    
    for evt in sources:
        eid = evt.get("idEvent")
        if not eid or eid in seen_ids:
            continue
        
        # Only keep within 3 days window
        date_str = evt.get("dateEvent")
        if date_str:
            try:
                evt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if abs((evt_date - today).days) > 3:
                    continue
            except ValueError:
                continue

        # Check if name is valid UFC
        event_name = get_event_name_from_torrent(evt.get("strEvent", ""))
        if event_name:
            # Filter by event_types
            if settings.event_types == "no_fightnights" and "Fight Night" in event_name:
                continue
                
            seen_ids.add(eid)
            combined.append(evt)

    return combined
