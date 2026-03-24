import logging
from qbittorrentapi import Client, LoginFailed, APIError
from ufc_fetcher.config import settings

logger = logging.getLogger(__name__)

def get_qbit_client():
    try:
        qbt = Client(**settings.qbittorrent_conn)
        qbt.auth_log_in()
        return qbt
    except LoginFailed as e:
        logger.error(f"qBittorrent login failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error connecting to qBittorrent: {e}")
        raise

def get_torrents() -> list:
    category = settings.qbittorrent_category
    try:
        with get_qbit_client() as qbt:
            return list(qbt.torrents_info(category=category))
    except Exception as e:
        logger.error(f"Error fetching torrents: {e}")
        return []

def add_torrent(url: str) -> bool:
    category = settings.qbittorrent_category

    try:
        with get_qbit_client() as qbt:
            qbt.torrents_add(
                urls=url,
                category=category,
            )
    
            return True
    except Exception as e:
        logger.error(f"Error adding torrent: {e}")
        return False
