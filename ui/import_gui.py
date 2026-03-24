import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import logging

from ..config import settings
from ..importer.manager import process_import

logger = logging.getLogger(__name__)

class ImportApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def run(self, infohash: str = ""):
        initial_dir = str(settings.downloads_path) if settings.downloads_path.exists() else None
        folder_path = filedialog.askdirectory(initialdir=initial_dir, title="Select UFC Download Folder to Import")
        self.root.destroy()

        if folder_path:
            logger.info(f"GUI: Importing from {folder_path}")
            imported = process_import(Path(folder_path), infohash=infohash)
            if imported:
                logger.info(f"GUI: Import complete. Imported to: {[str(p) for p in imported]}")
            else:
                logger.warning("GUI: No folders were imported.")
        else:
            logger.info("GUI: Import cancelled by user.")
