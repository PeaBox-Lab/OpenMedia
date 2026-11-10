# OpenMedia Lite v2.0.0 — Recovery & Bookmarks

The 2.0 milestone of the local-first, API-optional Browser Hub adds timestamp bookmarks, last-session recovery, focus/listening modes, and safer import previews while preserving the complete 1.x feature set.

## Added in 2.0

- Timestamp bookmarks for native video and audio
- Bookmark labels, optional notes, and precise seek-back actions
- Central bookmarks list with independent deletion
- Persistent last-session item and playback position
- Resume card shown in the empty player state
- Focus mode that reduces the interface to the player
- Listening mode that hides video imagery while keeping audio controls
- Import preview before any library data is merged
- Preview counts for media, duplicates, libraries, playlists, subscriptions, and reminders
- Explicit import confirmation
- Bookmark portability through library export/import and full backup

## Session behavior

Focus and listening modes are temporary viewing modes and are intentionally not persisted. Last-session recovery is persisted for saved web media and native-media progress records. Local files cannot be reopened after a browser restart unless the user selects them again.

## Import safety

Library import no longer changes data immediately after file selection. OpenMedia parses the file, shows a summary, reports duplicate IDs that will be skipped, and waits for explicit merge confirmation. Full backup restore remains a separate replacement workflow with its own confirmation.

## Retained

- Browser Hub and optional structured API discovery
- Playlists, tags, reminders, sharing, and accessibility controls
- Watch Later, subscriptions, ratings, notes, and insights
- Persistent queue, history, Continue Watching, and advanced playback controls
- Smart collections, command palette, maintenance, diagnostics, preferences, and backups
- Local media, responsive layouts, and PWA caching

## Run and test

Run `run_windows.bat` or `sh run_mac_linux.sh`, then open `http://127.0.0.1:8080`.

Run tests with `python -m unittest discover -s tests`.
