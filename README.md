# OpenMedia Lite v1.0.0

A zero-dependency, lightweight browser media player and library UI.

## Run
- Windows: double-click `run_windows.bat`.
- macOS/Linux: run `sh run_mac_linux.sh`.
- Or serve this folder with any static web server and open `index.html` through localhost/HTTPS.

## Features
- Local video, audio and image playback by file picker, folder picker, or drag and drop.
- URLs from YouTube, Dailymotion, Vimeo and SoundCloud using provider embeds.
- Direct HTTP(S) media URLs.
- Search, type views, favorites, session queue, grid/list layouts, libraries, dark/light modes.
- Keyboard controls: Space, left/right arrow, F.
- PWA shell caching when served over localhost/HTTPS.

## Important limitations
- Actual codec support is controlled by the browser/OS. MP4/H.264/AAC, WebM/VP8/VP9/Opus, MP3, WAV, Ogg, JPEG, PNG, GIF and WebP are common. MKV, AVI, HEVC, FLAC and AV1/AVIF support varies.
- This lightweight edition does not transcode unsupported codecs. A future desktop build can bundle libVLC or FFmpeg for broader format support.
- Local files are kept only for the current session. Library names persist locally, but file bytes are not uploaded or copied.
- Web providers may block embedding, require login, show ads, restrict regions, or disable a specific video. The app does not bypass provider controls or DRM.
- For Dailymotion production analytics/monetization, replace the basic iframe flow with a custom Player ID from Dailymotion Studio.

## Privacy
Local media is opened with browser object URLs and stays on the device. Web-video playback connects directly to the selected provider.
