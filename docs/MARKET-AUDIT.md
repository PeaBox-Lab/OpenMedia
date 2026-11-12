# OpenMedia — Market Audit, Gap Analysis & Roadmap

Prepared: 2026-11-13 · Current release: 2.0.0 → Roadmap target: 3.0.0

## 1. What OpenMedia is today

A local-first, API-optional "Browser Hub" for video/audio/image that:
- plays local files, pasted links (YouTube, Vimeo, Dailymotion, SoundCloud, direct URLs), and API-discovered media
- keeps a persistent web-media library in SQLite with queue, history, continue-watching, ratings, tags, notes, bookmarks, reminders, playlists, subscriptions, backups, command palette, maintenance, PWA caching
- binds to 127.0.0.1, encrypts optional API keys in a local vault

## 2. Market landscape (studied November 2026)

| App | Model | Strengths | Key gaps |
|---|---|---|---|
| Grayjay (FUTO) | Android, multi-source | "Follow creators, not platforms"; subscriptions across YouTube/Patreon/Twitch; no account needed; plugin sources | Mobile-only; no local files; no desktop library; no backup/restore discipline; no privacy-local vault |
| NewPipe / LibreTube / Tubular | Android, local | Privacy, background play, no Google account | YouTube-centric; mobile-only; brittle against site changes |
| FreeTube | Desktop, Electron | Privacy (no account, Invidious/Piped), subscriptions | YouTube + a few; heavyweight; no unified queue across providers; no local-media story |
| Invidious / Piped | Self-hosted frontends | Keyless YouTube via instances | Single platform; instance reliability varies |
| Kodi / Plex / Jellyfin | Media servers | Deep library management, transcoding | Not provider-browsers; no web-video unify; complexity |
| Browser + native apps | — | Always newest | Fragmented; no shared watch-later, queue, progress, notes across sites |

**Conclusion:** nobody offers a *local-first, cross-provider, desktop* hub that unifies local files + top web video sites + unified watch-later/queue/progress/notes, with zero required accounts.

## 3. USP (why OpenMedia wins)

1. **One local-first library** for local files **and** web video — nothing leaves the machine unless you choose.
2. **Keyless by default** — public search paths (Piped/Invidious for YouTube, Dailymotion public API, PeerTube federated search, Internet Archive, media.ccc.de, LBRY/Odysee) work with **no credentials at all**. API keys are an *upgrade*, never a requirement.
3. **Connect-your-account, not your secrets** — sign-in happens on the provider's own site in the in-app browser; OpenMedia never harvests passwords. Optional API keys are stored in an encrypted local vault with one-click links to each provider's key console.
4. **Provider-agnostic watch-later, queue, progress, notes, bookmarks** — the cross-site layer no single platform gives you.
5. **Portable** — full JSON backup/restore and library export; your curation outlives any app.

## 4. Gaps found in OpenMedia 2.0 (audit)

### Strengths (keep)
- Solid local vault, SQLite WAL, import preview, maintenance tools, accessibility prefs, command palette, PWA.

### Gaps (fix in 3.0)
- **G1 – Keyless discovery is under-used.** YouTube search *requires* an API key; in fact Piped/Invidious expose keyless search. Dailymotion search doesn't need a token at all. Internet Archive, media.ccc.de, Odysee/LBRY are entirely absent.
- **G2 – Provider coverage is tiny** (4 sites). The top video web is YouTube, Vimeo, Dailymotion, Twitch, TikTok, Reddit, Bilibili, Rumble, Odysee, PeerTube, SoundCloud, Internet Archive, Twitch, X, Instagram, Kick, Niconico, media.ccc.de.
- **G3 – No "Connect account" story.** Users are asked for API keys with no guidance. Need: per-provider sign-in (in-app browser), direct deep-links to key consoles, and a provider catalog with capabilities (search / embed / sign-in / API console / docs).
- **G4 – UI is functional but dated** — dense dark theme, emoji iconography, no design system, weak empty states, cramped provider strip.
- **G5 – parseWeb** only understands 5 providers; unknown sites are unplayable dead-ends. Add URL parsers + embed templates for the new catalog, and graceful fallback for "open externally".
- **G6 – No cross-provider search UX** — no provider filter chips, no capability badges, no "keyless" indicators.
- **G7 – Tests** only cover server happy paths; no provider-catalog or keyless-search contract tests.
- **G8 – Signage/versioning** — manifest/sw/README drift; no single source of truth for version.

## 5. Roadmap

### 3.0 (this build) — "Connected & Complete"
- Provider catalog (18 sites) in server (`/api/providers`) + in-app **Connect Accounts** dialog: sign-in link, API console deep-link, keyless badge, capability list, docs.
- **Keyless search**: Piped instances for YouTube (key optional upgrade), Dailymotion public, PeerTube federated, Internet Archive, media.ccc.de, LBRY/Odysee claim search. YouTube API key now optional.
- **Modern UI rebuild**: design tokens, Inter/system type scale, glass surfaces, gradient accent, focus-visible rings, refined cards/grid, proper empty states, skeleton loading, provider filter chips with capability badges.
- In-app browser gets provider shortcuts for all 18 sites; parseWeb gains Twitch/TikTok/Reddit/Bilibili/Rumble/Odysee/archive.org/ccc.de/Dailymotion/SoundCloud/NicoVideo embed support; unknown http(s) still opens externally.
- Version bump → 3.0.0 (server, manifest, sw cache, README, tests).
- Tests: provider catalog contract, keyless Dailymotion/PeerTube/Archive request shaping, settings/health, backup round-trip.

### 3.1 — "Follow"
- Subscription auto-refresh for Piped/Invidious/PeerTube feeds (keyless RSS-style), new-episodes inbox, per-subscription unread badges.
- Internet Archive collections & media.ccc.de conferences as channels.

### 3.2 — "Offline & Playback"
- Optional yt-dlp sidecar integration (user-installed) for offline saving of permitted content; background audio; media-session integration (lockscreen controls).
- Picture-in-picture, chapter markers, playback speed memory per media type.

### 3.3 — "Sync & Share"
- Optional end-to-end encrypted sync (user-supplied WebDAV/S3), library share links, collaborative playlists.
- OAuth device flows for providers that support it (Google/YouTube, Twitch) once user-supplied client IDs are entered.

### 3.4 — "Intelligence"
- On-device embeddings for "more like this", smart dedupe across providers (same video mirrored), auto-tagging, watch-time insights, weekly digest.

### Non-goals (for now)
- Hosting/transcoding (Kodi/Plex territory), DRM circumvention, credential harvesting, scraping sites that forbid it.

## 6. Risks & mitigations
- Provider API drift → provider catalog is data-driven (`/api/providers`); failures degrade to "open externally", never hard-fail.
- Piped instance availability → configurable instance list with automatic failover; YouTube API key remains as optional upgrade.
- ToS → sign-in uses provider pages in-browser; OpenMedia never stores provider passwords.
