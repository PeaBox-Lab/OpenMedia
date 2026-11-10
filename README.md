# OpenMedia Lite v1.2.0

The cumulative discovery release of the zero-dependency local media player.

## Run

- Windows: run `run_windows.bat`
- macOS/Linux: run `sh run_mac_linux.sh`
- Open `http://127.0.0.1:8080`

Python 3 is the only runtime dependency. Set provider credentials using the variable names in `.env.example`. Credentials stay on the localhost server and are never returned to the browser.

## Added in 1.2

- YouTube video, channel, and playlist search
- YouTube playlist expansion into playable videos
- Vimeo, Dailymotion, and federated PeerTube video discovery
- Provider, content type, duration, publication date, relevance, newest, and title controls
- Ten-minute in-memory cache for identical search and playlist requests
- Settings and provider-readiness dashboard
- Mixed web-library JSON export and import
- Provider-ID de-duplication during search and import
- Original provider links for playing web items
- Responsive desktop and mobile layouts

## Retained

Local video/audio/image playback, web embeds, direct media URLs, favorites, custom libraries, recently added sorting, session queue, dark/light themes, keyboard controls, PWA shell caching, and Windows/macOS/Linux launchers.

## Environment variables

- `YOUTUBE_API_KEY`
- `VIMEO_ACCESS_TOKEN`
- `DAILYMOTION_ACCESS_TOKEN`
- `PEERTUBE_INSTANCE` (defaults to `https://sepiasearch.org`)
- `OPENMEDIA_PORT` (defaults to `8080`)

## Limitations

Provider APIs, authentication, quotas, embedding permissions, regional restrictions, ads, and DRM remain controlled by each provider. Local file bytes are session-only and are intentionally excluded from export files.
