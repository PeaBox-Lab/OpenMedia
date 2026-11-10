# OpenMedia Lite v1.8.0 — Personal Media Workspace

A cumulative API-optional Browser Hub with persistent queue, smart collections, library maintenance, Watch Later, manual subscriptions, personal ratings and notes, and local usage insights.

## Added in 1.8

- Persistent Watch Later status and dedicated view
- Persistent one-to-five-star ratings and Rated view
- Personal notes for saved media items
- Manual subscriptions for creator, channel, profile, or provider pages
- Subscription shortcuts open through Browser Hub and require no API
- Remove subscriptions independently from saved media
- Local usage-insights dashboard
- Total and seven-day play counts
- Watch Later, subscription, rating, and progress summaries
- Average personal rating
- Most-played provider ranking based on saved playback history
- Command-palette shortcuts for Watch Later, Rated media, and Insights

## Privacy and data behavior

Subscriptions, ratings, notes, Watch Later state, and insights remain local in the existing SQLite-backed application state. Insights are calculated from OpenMedia history and progress records; no activity is sent to a remote analytics service.

Manual subscriptions are bookmarks, not background feed synchronization. They open the saved provider page through Browser Hub or its external fallback. Structured channel or playlist retrieval still requires an optional provider API where supported.

## Retained

- Browser Hub and pasted-link playback
- Optional API discovery
- Persistent queue, history, Continue Watching, playback controls, and mini-player
- Smart collections, command palette, full backup/restore, diagnostics
- Batch actions, durable deletion, duplicate cleanup, and preferences
- Local media, responsive themes, and PWA caching

## Run and test

Run `run_windows.bat` or `sh run_mac_linux.sh`, then open `http://127.0.0.1:8080`.

Run tests with `python -m unittest discover -s tests`.
