# OpenMedia Lite v1.3.0

A cumulative, zero-dependency local media player and multi-provider discovery app with persistent libraries and playback progress.

## Run

- Windows: run `run_windows.bat`
- macOS/Linux: run `sh run_mac_linux.sh`
- Open `http://127.0.0.1:8080`

Python 3 is the only runtime dependency. The server binds only to `127.0.0.1`.

## Added in 1.3

- SQLite-backed persistent web libraries, favorites, collections, and playback progress
- Continue Watching view with automatic resume positions for native video and audio
- Automatic progression to the next native video or audio item
- Persistent ten-minute API response cache
- Provider requests with bounded exponential-backoff retry
- First-run provider setup wizard and readiness dashboard
- Protected local provider-secret vault with integrity checking and restricted file permissions where supported
- Environment variables continue to override saved provider settings
- Storage, cache, and provider status in the health dashboard

## Retained from 1.2

- YouTube video, channel, and playlist search
- YouTube playlist expansion
- Vimeo, Dailymotion, and federated PeerTube discovery
- Provider, content type, duration, publication date, relevance, newest, and title controls
- JSON import/export and provider-ID de-duplication
- Original provider links
- Local video, audio, and image playback
- Favorites, libraries, queue, themes, keyboard controls, responsive layouts, and PWA shell caching

## Data and security notes

Application state is stored under the local `data` directory. Provider values entered through setup are protected at rest using an authenticated local vault and a randomly generated local key. This prevents plain-text storage and detects modification, but anyone with full access to both the application data and key files can recover the values. For stricter secret management, use environment variables or an operating-system credential manager.

Local files still remain session-only because browser object URLs cannot be restored after restart. Web items and their metadata can be persisted.

## Provider variables

- `YOUTUBE_API_KEY`
- `VIMEO_ACCESS_TOKEN`
- `DAILYMOTION_ACCESS_TOKEN`
- `PEERTUBE_INSTANCE`
- `OPENMEDIA_PORT`

## Automated smoke tests

Run `python -m unittest discover -s tests` from the release folder. The tests verify the health contract, SQLite-backed state, and playback progress endpoints. The test writes temporary records into the local application database; delete the `data` directory afterward if you want a clean first-run state.
