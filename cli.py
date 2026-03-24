import argparse
import logging
from pathlib import Path

from .config import settings
from .scanner.browse import collect_relevant_events
from .scanner.search import find_best_releases
from .core.qbit import add_torrent, get_torrents
from .importer.manager import process_import
from .importer.metadata import get_event_name_from_torrent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ufc_fetcher")

def cmd_find(args):
    """Find and queue upcoming UFC events."""
    logger.info("Checking for upcoming UFC cards...")
    events = collect_relevant_events()
    if not events:
        logger.info("No new events found.")
        return

    # Get already queued torrents to avoid duplicates
    existing_torrents = get_torrents()
    queued_names = [get_event_name_from_torrent(t.name) for t in existing_torrents]

    for evt in events:
        event_name = get_event_name_from_torrent(evt.get("strEvent", ""))
        date_str = evt.get("dateEvent", "?")
        
        if event_name in queued_names:
            logger.info(f"Skipping {event_name} ({date_str}) - already queued.")
            continue

        logger.info(f"Searching releases for {event_name}...")
        best_releases = find_best_releases(event_name)
        
        if not best_releases:
            logger.warning(f"No releases found for {event_name}")
            continue

        for release in best_releases:
            title = release.get("title")
            url = release.get("magnetUrl") or release.get("downloadUrl")
            if url:
                if add_torrent(url):
                    logger.info(f"Successfully queued: {title}")
                else:
                    logger.error(f"Failed to queue: {title}")

def cmd_import(args):
    """Import a completed download."""
    if args.path:
        path = Path(args.path)
        logger.info(f"Importing from {path}")
        imported = process_import(path, infohash=args.infohash)
        if imported:
            logger.info(f"Import complete. Imported to: {[str(p) for p in imported]}")
    else:
        # GUI Fallback
        from .ui.import_gui import ImportApp
        app = ImportApp()
        app.run(infohash=args.infohash)

def cmd_art(args):
    """Fetch artwork for an event folder."""
    if args.path:
        from .importer.art import fetch_art_for_folder
        path = Path(args.path)
        logger.info(f"Fetching artwork for {path}")
        fetch_art_for_folder(path)
    else:
        # GUI Fallback
        from .ui.art_fetcher import ArtFetcherApp
        app = ArtFetcherApp()
        app.run()

def main():
    parser = argparse.ArgumentParser(description="UFC Fetcher CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # find command
    find_parser = subparsers.add_parser("find", help="Scan for and queue upcoming events")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import a completed download")
    import_parser.add_argument("--path", help="Path to the downloaded file or folder. If omitted, a GUI picker will open.")
    import_parser.add_argument("--infohash", default="", help="Optional torrent infohash")

    # Art command
    art_parser = subparsers.add_parser("art", help="Launch the artwork fetcher GUI or provide a path")
    art_parser.add_argument("--path", help="Path to the UFC event folder. If omitted, a GUI picker will open.")

    args = parser.parse_args()

    if args.command == "find":
        cmd_find(args)
    elif args.command == "import":
        cmd_import(args)
    elif args.command == "art":
        cmd_art(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
