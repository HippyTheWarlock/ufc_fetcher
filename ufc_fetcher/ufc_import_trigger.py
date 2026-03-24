import argparse
import subprocess
import logging
from ufc_fetcher.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ufc_trigger")

def main():
    parser = argparse.ArgumentParser(description="UFC Fetcher qBittorrent Trigger")
    parser.add_argument("--category", required=True, help="Torrent category")
    parser.add_argument("--path", required=True, help="Content path")
    parser.add_argument("--infohash", required=True, help="Torrent infohash")
    
    args = parser.parse_args()
    
    target_category = settings.qbittorrent_category
    
    logger.info(f"Triggered for category: {args.category}")
    
    if args.category == target_category:
        logger.info(f"Category matches '{target_category}'. Running import...")
        try:
            # Call the cli command
            # Using 'ufc-fetcher' assumes it's in the system path
            cmd = ["ufc-fetcher", "import", "--path", args.path, "--infohash", args.infohash]
            subprocess.run(cmd, check=True)
            logger.info("Import completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Import failed with error: {e}")
        except FileNotFoundError:
            logger.error("Error: 'ufc-fetcher' command not found. Ensure the package is installed.")
    else:
        logger.info(f"Category '{args.category}' does not match '{target_category}'. Skipping.")

if __name__ == "__main__":
    main()
