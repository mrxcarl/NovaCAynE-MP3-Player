# 🎵 NovaCAynE Music Player
**Elevate your listening experience with a sleek, high-performance desktop powerhouse.**
NovaCAynE isn't just a music player; it's a polished experience for those who demand a premium aesthetic without sacrificing functionality. Built with a "Dark Mode" first philosophy, it combines a sophisticated UI with a robust backend to deliver a seamless, distraction-free way to enjoy your tunes.
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![Framework](https://img.shields.io/badge/GUI-CustomTkinter-blue.svg)
![Discord](https://img.shields.io/badge/Discord-RPC-5865F2?logo=discord)
---
## ✨ Features
*   **🌑 Midnight Aesthetic:** A gorgeous, "dark-mode" first interface built on `customtkinter` for that premium, modern feel.
*   **📂 Smart Library Management:** Effortlessly import single tracks or dump entire folders into your library with one click.
*   **🔍 Deep Metadata Extraction:** No more "Unknown Artist" vibes. `mutagen` automatically grabs and displays track titles and artist details.
*   **🚀 Discord Presence (RPC):** Show off what you're listening to! Integrated Discord Rich Presence keeps your profile updated in real-time.
*   **⏭ Seamless Flow:** Auto-advance features ensure the music never stops when a track ends.
*   **🎚 Precision Control:** Smooth volume scaling, real-time progress tracking, and responsive playback toggles.
*   **🧹 Clean House:** Quick-action buttons to prune specific tracks or wipe the slate clean.
*   **🔄 Auto-Updater (Coming Soon):** An automated update system is in development to keep your experience fresh and up-to-date effortlessly.

## 🚀 The Tech Stack
*   **Python** — The brain behind the operation.
*   **Pygame** — Powering the heavy lifting of audio processing.
*   **CustomTkinter** — Crafting the high-end UI components.
*   **Mutagen** — The expert in ID3 Tag metadata extraction.
*   **Pillow** — Handling the visual branding and assets.
*   **PyPresence** — Syncing your vibe directly to Discord.

## 🛠 Getting Started
### Prerequisites
Make sure you have **Python 3.10** or higher installed before diving in.
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/NovaCAynE-Player.git
    cd NovaCAynE-Player
    ```
2.  **Install the Dependencies**
    ```bash
    pip install pygame customtkinter mutagen Pillow pypresence
    ```
3.  **Launch the Beast**
    ```bash
    python mp3player.py
    ```
## 📦 Build the Executable
Want to run it as a standalone app without the terminal in your face? Let's package it.
1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Build the EXE:**
    Run the magic command (ensure your `logo.png` and `icon.ico` are in the root folder):
    ```bash
    pyinstaller --noconsole --onefile --add-data "logo.png;." --icon="icon.ico" mp3player.py
    ```
    *Note: If you're rocking a Mac or Linux, swap that semicolon `;` for a colon `:` in the `--add-data` flag.*
## 📂 Project Structure
```text
NovaCAynE/
├── mp3player.py         # The heart of the application
├── logo.png             # UI Branding (352x192)
├── icon.ico             # Window icon
├── requirements.txt     # Dependency list
└── README.md            # The manual
```
## 🤝 Contribute
Got a wild idea for a feature? Want to tweak the UI? Pull requests are legendary. Feel free to fork the repo and let's build something cool together.
## 📜 License
This project is licensed under the MIT License. Check the [LICENSE](LICENSE) file for the nitty-gritty.
---
**Developed by JethroTeK**  
*Refining the way you hear music.*
