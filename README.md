# UFC Fetcher

A unified tool for automatically finding, downloading, and importing UFC events into your media library.

## Features

- **Find**: Automatically scans for recent UFC events and queues them in qBittorrent.
- **Import**: Automatically renames and moves completed downloads into your library with KODI-compatible NFO files.
- **Art**: A simple GUI to manually fetch missing artwork for your event folders.

## Compatibility

Requires Prowlarr integration to search for releases. Currently the only compatible torrent client is qBittorrent.

## Installation

```bash
cd "UFC Fetcher"
pip install .
```

## Configuration

The tool loads configuration from `~/.ufc_fetcher/config.json`. You can also use environment variables prefixed with `UFC_FETCHER_`.

### Example `config.json`

```json
{
  "prowlarr_url": "http://localhost:9696",
  "prowlarr_api_key": "YOUR_PROWLARR_KEY",
  "qbittorrent_host": "localhost",
  "qbittorrent_port": 8080,
  "qbittorrent_username": "your_user",
  "qbittorrent_password": "your_password",
  "qbittorrent_category": "UFC",
  "library_path": "D:\\library\\UFC",
  "downloads_path": "D:\\downloads\\UFC",
  "sports_db_url": "https://www.thesportsdb.com/api/v1/json/123",
  "language_preference": "en", // ISO 639-1 code (e.g., "en", "ru"). Leave blank for no preference.
  "quality_preference": "1080", // Options: "480", "720", "1080". Leave blank for no preference.
  "codec_preference": "x265", // Options: "x264", "x265". Leave blank for no preference
  "event_types": "all", // Options: "all", "no_fightnight". If no_fightnight is selected, only numbered events (e.g., UFC 300) will be fetched. Defaults to all if blank.
  "full_or_main": "full" // Options: "full", "main_only". Full prefers releases with all cards (early prelims, prelims, and main), main_only prefers releases with just the main card. Defaults to full if blank.
}
```

## Usage

### Find New Events
```bash
ufc-fetcher find
```

### Import a Download
```bash
# Provide a path directly:
ufc-fetcher import --path "D:\downloads\UFC\UFC.300.720p.WEB.h264"

# Or launch a GUI folder picker:
ufc-fetcher import
```

### Fetch Artwork
```bash
# Provide a path directly:
ufc-fetcher art --path "D:\library\UFC\UFC 300"

# Or launch a GUI folder picker:
ufc-fetcher art
```

## Automating Imports (qBittorrent)

To automatically import downloads when they finish:
1. Set `qbittorrent_category` in config.json to your desired category name (default is "UFC").
2. In qBittorrent, go to **Tools** > **Options** > **Downloads**.
3. Check **Run external program** > **Run on torrent finished**.
4. Enter the following command (set path to your install location):
   ```bash
   python "C:\Program Files\ufc_fetcher\ufc_import_trigger.py" --category "%L" --path "%F" --infohash "%I"
   ```
