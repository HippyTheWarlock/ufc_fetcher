import requests
import logging
import xmltodict
from pathlib import Path

logger = logging.getLogger(__name__)

def fetch_art_for_folder(folder_path: Path):
    """Fetch artwork based on the tvshow.nfo in the folder."""
    nfo_path = folder_path / "tvshow.nfo"
    if not nfo_path.exists():
        logger.error(f"tvshow.nfo not found in {folder_path}")
        return

    try:
        with open(nfo_path, 'r', encoding='utf-8') as f:
            nfo_data = xmltodict.parse(f.read())
        
        art_dict = nfo_data.get('tvshow', {}).get('art', {})
        if not art_dict:
            logger.warning(f"No artwork metadata found in {nfo_path}")
            return

        for art_type, url in art_dict.items():
            if not url: continue
            
            # Basic sanitization of filenames
            dest = folder_path / f"{art_type}.jpg"
            if dest.exists():
                logger.info(f"Artwork {art_type}.jpg already exists, skipping")
                continue

            logger.info(f"Downloading {art_type} from {url}")
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200:
                    with open(dest, 'wb') as f:
                        f.write(resp.content)
                    logger.info(f"Saved {art_type} to {dest}")
                else:
                    logger.error(f"Failed to download {art_type}: {resp.status_code}")
            except Exception as e:
                logger.error(f"Error downloading {art_type}: {e}")

    except Exception as e:
        logger.error(f"Error processing NFO for art in {folder_path}: {e}")
