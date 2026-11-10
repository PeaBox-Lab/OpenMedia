# OpenMedia Lite v1.5.0 — Persistent Queue

A cumulative API-optional browser and media hub with persistent libraries, playback progress, history, and a user-managed queue.

## Run

- Windows: run `run_windows.bat`
- macOS/Linux: run `sh run_mac_linux.sh`
- Open `http://127.0.0.1:8080`

Python 3 is the only runtime dependency. The server binds only to `127.0.0.1`.

## Added in 1.5

- Persistent user-managed play queue for saved web media
- Persistent playback history with a dedicated History view
- Queue all and shuffle-all actions
- Remove individual queue entries without deleting library items
- Previous and next navigation
- Repeat off, repeat all, and repeat one
- Shuffle playback mode
- Native audio/video playback speeds from 0.75× to 2×
- Native audio/video mute control
- Compact floating mini-player mode
- Queue count and currently-playing highlight
- Automatic queue progression now respects repeat and shuffle modes

## Retained

- API-optional Browser Hub and provider shortcuts
- Supported pasted-link playback for YouTube, Vimeo, Dailymotion, SoundCloud, PeerTube, and direct media URLs
- Optional structured API discovery
- SQLite libraries, favorites, Continue Watching, and playback progress
- JSON import/export, local media, responsive themes, keyboard controls, and PWA caching

## Notes

The persistent queue stores saved web-item identifiers. Local files cannot survive a browser restart and therefore are not restored into a later session's queue. Third-party websites may still block the Browser Hub frame; use the external fallback and paste a supported final media URL into OpenMedia.

## Tests

Run `python -m unittest discover -s tests`.
