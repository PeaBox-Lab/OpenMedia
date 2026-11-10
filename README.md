# OpenMedia Lite v1.7.0 — Library Maintenance

A cumulative API-optional Browser Hub with smart collections, persistent queues, full backup/restore, batch library actions, and safe maintenance controls.

## Added in 1.7

- Multi-select mode for media cards
- Select-all within the active filtered view
- Batch favorite, queue, library assignment, and deletion
- Durable saved-item and library deletion in SQLite
- Duplicate URL analysis and merging
- Incomplete saved-item detection and removal
- Clear playback history, Continue Watching progress, or API cache independently
- Persistent appearance preference: dark, light, or system
- Comfortable and compact library density
- Configurable automatic queue advancement
- Configurable deletion confirmations
- Maintenance statistics for items, duplicates, incomplete records, and history

## Safety and persistence

Batch deletion, duplicate merging, incomplete-item cleanup, history clearing, progress clearing, and cache clearing require explicit confirmation where appropriate. The server now treats saved-item lists as authoritative during state synchronization, so deleted web items no longer return after restart.

## Retained

- Browser Hub with API-free provider shortcuts and supported-link playback
- Optional structured API discovery
- Smart provider collections and global command palette
- Persistent queue, history, Continue Watching, repeat, shuffle, speed, mute, and mini-player controls
- Full backup/restore and diagnostics
- SQLite libraries and protected optional credentials
- Local media, responsive themes, and PWA caching

## Run and test

Run `run_windows.bat` or `sh run_mac_linux.sh`, then open `http://127.0.0.1:8080`.

Run tests with `python -m unittest discover -s tests`.
