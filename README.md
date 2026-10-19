# NovaCAynE Player

A sleek, modern Python-based music player with a custom UI, Discord Rich Presence integration, and seamless YouTube integration.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repo-blue?style=flat-square&logo=github)](https://github.com/mrxcarl/NovaCAynE-MP3-Player)

## 🚀 Features
- **Modern UI**: Built with `customtkinter` for a sleek, high-quality dark-themed experience.
- **Local Playback**: Easily load individual `.mp3` files or entire music folders into your library.
- **YouTube Integration**: 
    - **Link Support**: Paste a YouTube URL to download and add a track instantly.
    - **Search Support**: Search directly by Artist and Track name to find and download music from the web.
- **Discord Rich Presence**: Show off what you're listening to! Integrates with Discord to display the current Artist and Track on your profile.
- **Advanced Controls**:
    - **Seek Functionality**: A responsive slider to jump to any part of the track.
    - **Quick Skip**: Dedicated buttons to Rewind (⏪) or Fast Forward (⏩) by 15 seconds.
- **Auto-Management**: Automatically manages the `downloads` folder and cleans up previous temporary files to keep your system tidy.

## 🛠 Tech Stack
- **Language:** Python
- **UI Framework:** CustomTkinter
- **Audio Engine:** Pygame Mixer
- **Metadata Handling:** Mutagen
- **YouTube Downloader:** yt-dlp
- **Discord RPC:** PyPresence

## 📋 Requirements
To run this application, you will need:
- Python 3.x
- FFmpeg (required by yt-dlp to process audio)

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/mrxcarl/NovaCAynE-MP3-Player.git
   ```
2. **Install the dependencies:**
   ```bash
   pip install pygame customtkinter mutagen Pillow pypresence yt_dlp
   ```
3. **Run the application:**
   ```bash
   python mp3player.py
   ```

## 📜 Changelog

### [Latest Update]
- **UI Overhaul**: Replaced the basic progress bar with a fully interactive **Seek Slider**.
- **Enhanced Controls**: Added **Rewind (⏪)** and **Fast Forward (⏩)** buttons for 15-second skips.
- **Search Integration**: Added a "Search by Artist/Track" feature to streamline the YouTube search process.
- **Auto-Cleanup**: Implemented logic to automatically clear previous downloads and ensure a clean workspace.
- **Progress Tracking**: Added a status label and progress hooks to provide real-time feedback during downloads.
- **Improved Reliability**: Enhanced the seek logic and multi-threading for a smoother user experience.

---
*Developed by JethroTeK*