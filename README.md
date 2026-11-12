# OpenMedia Lite v3.0.0 — Connected & Complete

The 3.0 milestone of the local-first, API-optional Browser Hub adds a full provider catalog for the web's top video sites, keyless search paths, one-click "Connect accounts" onboarding, and a modern visual rebuild — while preserving the complete 2.x feature set and local-first guarantees.

## Added in 3.0

- **Provider catalog (18 sites)** served by `/api/providers`: YouTube, Vimeo, Dailymotion, PeerTube, SoundCloud, Twitch, TikTok, Reddit, Bilibili, Rumble, Odysee, Internet Archive, media.ccc.de, Kick, Niconico, X (Twitter), Instagram, Piped/Invidious
- **Keyless search everywhere possible**: YouTube via Piped federation (API key optional upgrade), Dailymotion public API, PeerTube federated search, Internet Archive advancedsearch, media.ccc.de frab API, LBRY/Odysee claim_search
- **Connect accounts dialog** — per-provider sign-in (opens on the provider's own site in the hub; OpenMedia never sees passwords), direct deep-links to each API console, "Keyless / Ready / Needs key" badges, capability tags, docs links
- **Rich link paste support**: embed templates for Twitch (channels & VODs & clips), TikTok, Reddit, Bilibili, Odysee, archive.org, Niconico, Kick, X/Twitter, Instagram
- **Modern UI layer**: design tokens, ambient gradient backdrop, gradient accent system, pill search, glass sticky header, provider strip with branded marks and capability badges, focus-visible rings, refined cards, dialog animations, custom scrollbars
- **Provider filter chips** for every catalog site in both the Browser Hub (scrollable branded strip) and API Discovery
- Version bump → 3.0.0 across server, service worker cache, manifest, README, and tests

## Roadmap (see docs/MARKET-AUDIT.md)

- **3.1 Follow**: keyless subscription auto-refresh (Piped/Invidious/PeerTube feeds), new-episodes inbox, unread badges
- **3.2 Offline & Playback**: optional yt-dlp sidecar for permitted offline saves, Media Session/lockscreen controls, picture-in-picture
- **3.3 Sync & Share**: optional E2E-encrypted sync (WebDAV/S3), share links, collaborative playlists, OAuth device flows for Google/YouTube and Twitch with user-supplied client IDs
- **3.4 Intelligence**: on-device "more like this", cross-provider smart dedupe, auto-tagging, weekly digest

## Retained

- Browser Hub and optional structured API discovery with encrypted local vault
- Local files, folder import, drag & drop, paste-to-add, direct URLs
- Playlists, libraries, smart collections, tags, ratings, notes, reminders, subscriptions
- Watch Later, history, Continue Watching, persistent queue, shuffle/repeat, timestamp bookmarks, session recovery, focus/listening modes
- Backups, import preview, maintenance tools, command palette, accessibility controls, PWA caching

## Run and test

Run `run_windows.bat` or `sh run_mac_linux.sh`, then open `http://127.0.0.1:8080`.

Run tests with `python -m unittest discover -s tests`.

## USP

**One local-first library for local files and the top video sites of the web — no account required, keys optional, data portable.** Details and the full competitive analysis live in `docs/MARKET-AUDIT.md`.
