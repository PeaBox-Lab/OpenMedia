# OpenMedia Lite v1.1.0

A zero-dependency local media player with server-backed discovery across configured video providers.

## Run

- Windows: run `run_windows.bat`
- macOS/Linux: run `sh run_mac_linux.sh`
- Open `http://127.0.0.1:8080`

Python 3 is the only runtime dependency. Provider credentials are read from environment variables and are never sent to the browser. Copy the names from `.env.example` into your shell environment before launching.

## Added in 1.1

- Localhost-only Python application server
- Unified provider search endpoint
- YouTube video discovery with an API key
- Vimeo and Dailymotion video discovery with access tokens
- Federated PeerTube discovery
- Search-result playback, provider labels, thumbnails, and source links
- Duplicate prevention for provider results

## Retained

Local video/audio/image playback, web embeds, direct URLs, favorites, libraries, session queue, drag and drop, keyboard controls, PWA shell, and responsive dark/light layouts.

## Limitations

Provider availability depends on configuration and provider responses. The app does not bypass authentication, embedding restrictions, regional controls, advertising, or DRM. Local files remain session-only.
