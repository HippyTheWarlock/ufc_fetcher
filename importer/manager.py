import shutil
import logging
from pathlib import Path
from typing import List
from filetype import guess

from ..config import settings
from ..importer.metadata import get_event_name_from_torrent, fetch_event_info, write_nfo, CARD_TYPES
from .art import fetch_art_for_folder

logger = logging.getLogger(__name__)

def get_card_type(filename: str) -> int:
    fname = filename.lower()
    if any(x in fname for x in ["countdown", "weigh.in", "interview", "conference", "preview"]):
        return 0
    if "early" in fname:
        return 1
    if "prelim" in fname:
        return 2
    return 3

def process_import(input_path: Path, infohash: str = "") -> List[Path]:
    """Process a completed download and import into the library."""
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return []

    imported_folders = []
    
    # Collect video files
    files_to_process = []
    if input_path.is_file():
        files_to_process.append(input_path)
    else:
        for p in input_path.rglob("*"):
            if p.is_file() and not p.name.startswith('.'):
                kind = guess(str(p))
                if kind and kind.mime.startswith('video'):
                    files_to_process.append(p)


    for file_p in files_to_process:
        event_name = get_event_name_from_torrent(file_p.name)
        if not event_name:
            # Try parent folder name
            event_name = get_event_name_from_torrent(file_p.parent.name)
        
        if not event_name:
            logger.warning(f"Could not determine event name for {file_p}")
            continue

        # Fetch metadata
        nfo_data = fetch_event_info(event_name)
        if not nfo_data:
            logger.error(f"Failed to fetch metadata for {event_name}")
            continue

        target_event_dir = settings.library_path / nfo_data['cleantitle'].strip()
        if target_event_dir not in imported_folders:
            imported_folders.append(target_event_dir)

        card_type = get_card_type(file_p.name)
        
        # Write generic tvshow.nfo if it doesn't exist
        write_nfo(nfo_data, target_event_dir, card_type=0)
        
        # Write specific episode nfo
        write_nfo(nfo_data, target_event_dir, card_type=card_type, infohash=infohash, releasename=file_p.name)
        
        # Copy file
        ext = file_p.suffix[1:]
        new_name = f"{nfo_data['cleantitle']} - {CARD_TYPES[card_type]}.{ext}"
        dest_p = target_event_dir / new_name
        
        logger.info(f"Importing {file_p.name} to {dest_p}")
        try:
            shutil.copy2(file_p, dest_p)
        except Exception as e:
            logger.error(f"Failed to copy {file_p} to {dest_p}: {e}")

    # Automatically fetch artwork for each imported folder
    for folder in imported_folders:
        logger.info(f"Fetching artwork for {folder.name}...")
        fetch_art_for_folder(folder)

    return imported_folders
