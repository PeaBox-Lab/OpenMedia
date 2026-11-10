# OpenMedia Lite v1.6.0 — Smart Library

A cumulative API-optional Browser Hub with persistent queue, playback history, smart collections, command search, full backup/restore, and diagnostics.

## Added in 1.6

- Automatic smart collections grouped by provider
- Recently Played view covering the last seven days of recorded playback
- Global command palette opened with `Ctrl+K` or `Command+K`
- Command search across media and common application actions
- Keyboard navigation through palette results
- Full JSON backup including libraries, saved media, progress, queue, history, and preferences
- Controlled backup restore with confirmation
- Local diagnostics dashboard for version, uptime, database size, table counts, vault status, and server binding
- Copyable diagnostics summary for support

## Retained

- API-optional provider Browser Hub
- Supported pasted-link playback and external fallback
- Persistent queue, history, repeat, shuffle, speed, mute, and mini-player controls
- SQLite libraries, favorites, Continue Watching, and playback progress
- Optional structured provider discovery and protected credentials
- Local media, JSON library portability, responsive themes, and PWA caching

## Run

- Windows: run `run_windows.bat`
- macOS/Linux: run `sh run_mac_linux.sh`
- Open `http://127.0.0.1:8080`

Python 3 is the only runtime dependency. The app binds only to `127.0.0.1`.

## Backup behavior

A full backup includes restorable web-media state and application preferences. Local file bytes are not included because browser-selected files are session-only. Restoring a full backup replaces saved libraries, web items, progress, queue, history, and preferences; it does not change provider credentials.

## Tests

Run `python -m unittest discover -s tests`.
