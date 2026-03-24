import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from pathlib import Path

from ufc_fetcher.config import settings
from ufc_fetcher.importer.art import fetch_art_for_folder

class ArtFetcherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def run(self):
        initial_dir = str(settings.library_path) if settings.library_path.exists() else None
        folder_path = filedialog.askdirectory(initialdir=initial_dir, title="Select UFC Event Folder")
        self.root.destroy()

        if folder_path:
            fetch_art_for_folder(Path(folder_path))
