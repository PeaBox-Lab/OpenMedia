# OpenMedia Lite v1.4.0 — Browser Hub

A modern, API-optional media hub for local files, provider browsing, pasted-link playback, persistent libraries, queues, and Continue Watching.

## Run

- Windows: run `run_windows.bat`
- macOS/Linux: run `sh run_mac_linux.sh`
- Open `http://127.0.0.1:8080`

Python 3 is the only runtime dependency. The server binds only to `127.0.0.1`.

## Do I need APIs?

No API is required for local media, direct media URLs, pasted supported provider links, Browser Hub search shortcuts, libraries, favorites, queues, and Continue Watching.

APIs remain optional for combined structured results inside OpenMedia, result metadata and thumbnails, filters, channels, and playlist expansion.

## Browsing model

Browser Hub attempts to display provider pages in its built-in panel. The attached v1.3 project already notes that providers can block embedding or require the original provider page. When a page does not appear, choose **Open externally**, navigate to a video, copy its URL, and paste it into OpenMedia for supported playback.

The release therefore uses a hybrid workflow: in-app browsing when permitted, external fallback when blocked, and dedicated embedded players for supported media links.

## Added in 1.4

- API-optional Browser Hub as the default experience
- Unified provider search and address bar
- Provider launch cards for YouTube, Vimeo, Dailymotion, PeerTube, and SoundCloud
- Built-in browsing panel with address display, home, back, and external fallback
- Automatic conversion of supported pasted links into in-app players
- Optional API Discovery retained in a separate tab
- Updated responsive visual system
- No forced first-run API setup

## Retained from 1.3

- SQLite-backed persistent web libraries and favorites
- Playback progress and Continue Watching
- Automatic native-media queue progression
- Persistent API cache and retry handling
- Protected optional credential storage
- Local media, JSON import/export, themes, keyboard controls, and PWA caching

## Tests

Run `python -m unittest discover -s tests`.
