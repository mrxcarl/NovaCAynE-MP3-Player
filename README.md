# 🎵 NovaCAynE Music Player

A sleek, modern, and high-performance desktop music player built with Python. NovaCAynE combines a polished "Dark Mode" aesthetic with a robust backend to provide a seamless listening experience.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![Framework](https://img.shields.io/badge/GUI-CustomTkinter-blue.svg)

---

## ✨ Features
- **Modern UI:** Designed with a "dark-mode" aesthetic using `customtkinter` for a premium, modern look.
- **Dynamic Library:** Easily import individual tracks or entire music folders into your playlist.
- **Real-time Metadata:** Automatically fetches Artist and Track details using `mutagen`.
- **Auto-Advance:** Automatically play the next track in your queue when the current one ends.
- **Smooth Controls:** Integrated progress tracking, volume control, and playback toggling.
- **Management Tools:** Quick actions to remove specific tracks or clear the entire library.

## 🚀 Technologies Used
- **Python** - Core logic
- **Pygame** - Audio processing and playback
- **CustomTkinter** - Modern UI components
- **Mutagen** - ID3 Tag metadata extraction
- **Pillow** - Image processing for branding

## 📸 Preview
*(Replace this with a screenshot or a GIF of your app once you upload it!)*
> "A sleek interface designed for a premium experience."

## 🛠 Installation

### Prerequisites
Ensure you have Python 3.10 or higher installed on your system.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/NovaCAynE-Player.git
   cd NovaCAynE-Player
   ```

2. **Install dependencies:**
   ```bash
   pip install pygame customtkinter mutagen Pillow
   ```

3. **Run the application:**
   ```bash
   python mp3player.py
   ```

## 📦 Building the Executable
To package the application into a single `.exe` file including all assets (logo, icons, and libraries):

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the EXE:**
   Run the following command (ensure your `logo.png` and `icon.ico` are in the folder):
   ```bash
   pyinstaller --noconsole --onefile --add-data "logo.png;." --icon="icon.ico" mp3player.py
   ```
   *Note: If you are on Mac/Linux, change the semicolon (`;`) to a colon (`:`) in the `--add-data` flag.*

## 📂 Project Structure
```text
NovaCAynE/
├── mp3player.py         # Main application script
├── logo.png             # UI Logo (352x192)
├── icon.ico             # Window icon
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## 🤝 Contributing
Contributions are welcome! If you have ideas for new features or UI improvements, feel free to fork the repository and submit a pull request.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Developed by JethroTeK**  
*Refining the way you hear music.*