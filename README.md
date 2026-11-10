# OpenMedia Lite v1.9.0 — Playlists & Accessibility

A cumulative local-first, API-optional Browser Hub with custom playlists, tags, watch reminders, link sharing, and expanded accessibility preferences.

## Added in 1.9

- Persistent custom playlists
- Batch-add selected media to a playlist
- Playlist playback through the persistent queue
- Remove individual playlist entries without deleting media
- Persistent item tags shown on library cards
- Tags included in library export and import
- Local watch reminders with optional browser notifications while the app is running
- Reminder list and independent reminder removal
- Device share-sheet support where available
- Clipboard link-copy fallback
- Reduced-motion preference
- High-contrast interface preference
- Larger-text preference
- Accessibility preferences persist in backups and across restarts

## Reminder behavior

Reminders are stored locally and checked while OpenMedia is running. Browser notifications are shown only if notification permission was already granted; otherwise an in-app message appears. This release does not install an operating-system background scheduler, so reminders do not fire while the app is closed.

## Sharing behavior

Sharing includes only the currently playing item's original source link and title. It does not upload personal notes, ratings, history, playlists, or library data.

## Retained

- Browser Hub, pasted-link playback, and optional API discovery
- Watch Later, subscriptions, ratings, notes, and local insights
- Persistent queue, history, Continue Watching, and player controls
- Smart collections, command palette, backup/restore, diagnostics
- Batch operations, durable deletion, cleanup, and preferences
- Local media and PWA caching

## Run and test

Run `run_windows.bat` or `sh run_mac_linux.sh`, then open `http://127.0.0.1:8080`.

Run tests with `python -m unittest discover -s tests`.
