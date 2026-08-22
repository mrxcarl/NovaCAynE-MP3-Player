import os
import sys
import threading
import time
import pygame
import customtkinter as ctk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.mp3 import EasyMP3
from PIL import Image, ImageTk

# Included as many comments as I could think of to explain things

# --- PyInstaller Path Handling ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

# Setup appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration ---
        self.title("NovaCAynE Player By: JethroTeK")
        self.geometry("1100x750")

        # Setup Window Icon (requires icon.ico in the folder)
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except:
            pass # Ignore if .ico is missing during development

        # Initialize Pygame Mixer
        pygame.mixer.init()

        # State Variables
        self.playlist = []
        self.current_track_index = -1
        self.is_playing = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)

        # Threading for Progress Bar and Auto-advance
        self.update_thread = threading.Thread(target=self.update_engine, daemon=True)
        self.update_thread.start()

        # --- UI Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Left Frame (Playlist / Sidebar) ---
        self.playlist_frame = ctk.CTkFrame(self, width=350, fg_color="#1a1a1a")
        self.playlist_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Logo Image Loading
        self.logo_img = None
        try:
            img_path = resource_path("logo.png")
            img = Image.open(img_path)
            # Optional: force resize to your specific dimensions
            # img = img.resize((352, 192)) 
            self.logo_img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Notice: Logo image not found or failed to load: {e}")

        # Logo Display (Place your logo here)
        if self.logo_img:
            self.logo_label = ctk.CTkLabel(self.playlist_frame, image=self.logo_img, text="")
            self.logo_label.pack(pady=(20, 10))
        
        self.label_list = ctk.CTkLabel(
            self.playlist_frame, 
            text="LIBRARY", 
            font=("Arial", 28, "bold"), 
            text_color="#3b82f6"
        )
        self.label_list.pack(pady=(0, 20), padx=20)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.playlist_frame, 
            width=320, 
            fg_color="#242424"
        )
        self.scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Sidebar Action Buttons
        self.btn_add_files = ctk.CTkButton(
            self.playlist_frame, 
            text="Add Individual Songs", 
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=("Arial", 13, "bold"),
            height=35
        )
        self.btn_add_files.pack(side="bottom", pady=(0, 5), padx=20)

        self.btn_add_folder = ctk.CTkButton(
            self.playlist_frame, 
            text="Add Music Folder", 
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=("Arial", 13, "bold"),
            height=35
        )
        self.btn_add_folder.pack(side="bottom", pady=(0, 5), padx=20)

        self.btn_remove_current = ctk.CTkButton(
            self.playlist_frame, 
            text="Remove Selected", 
            fg_color="#eab308",
            hover_color="#ca8a04",
            font=("Arial", 13, "bold"),
            height=35
        )
        self.btn_remove_current.pack(side="bottom", pady=(0, 5), padx=20)

        self.btn_clear_all = ctk.CTkButton(
            self.playlist_frame, 
            text="Clear All", 
            fg_color="#dc3545",
            hover_color="#bc2030",
            font=("Arial", 13, "bold"),
            height=35
        )
        self.btn_clear_all.pack(side="bottom", pady=(0, 10), padx=20)

        # --- Right Frame (Main Player) ---
        self.player_frame = ctk.CTkFrame(self, fg_color="#121212")
        self.player_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        self.track_label = ctk.CTkLabel(
            self.player_frame, 
            text="No Track Selected", 
            font=("Arial", 36, "bold")
        )
        self.track_label.pack(pady=(80, 10))

        self.artist_label = ctk.CTkLabel(
            self.player_frame, 
            text="Select a song to start", 
            font=("Arial", 18), 
            text_color="gray"
        )
        self.artist_label.pack(pady=(0, 40))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.player_frame, width=500, progress_color="#3b82f6")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Controls Row
        self.controls_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.controls_frame.pack(pady=30)

        self.btn_prev = ctk.CTkButton(
            self.controls_frame, text="⏮", width=60, height=60, 
            font=("Arial", 30), fg_color="#2d2d2d", hover_color="#3d3d3d",
            command=self.prev_track
        )
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.btn_play = ctk.CTkButton(
            self.controls_frame, text="▶", width=100, height=60, 
            font=("Arial", 30, "bold"), fg_color="#3b82f6",
            command=self.toggle_play
        )
        self.btn_play.grid(row=0, column=1, padx=10)

        self.btn_next = ctk.CTkButton(
            self.controls_frame, text="⏭", width=60, height=60, 
            font=("Arial", 30), fg_color="#2d2d2d", hover_color="#3d3d3d",
            command=self.next_track
        )
        self.btn_next.grid(row=0, column=2, padx=10)

        # Volume Slider
        self.volume_slider = ctk.CTkSlider(self.player_frame, from_=0, to=1, width=400, command=self.set_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(pady=20)

    # --- Core Engine Logic ---
    def add_files(self):
        files = filedialog.askopenfilenames(title="Select MP3 Files", filetypes=[("MP3 Files", "*.mp3")])
        if files:
            self.update_playlist(list(files))

    def add_folder(self):
        path = filedialog.askdirectory(title="Select Music Folder")
        if path:
            files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".mp3")]
            if files:
                self.update_playlist(files)

    def update_playlist(self, new_files):
        self.playlist.extend(new_files)
        self.playlist = list(set(self.playlist))  # Remove duplicates
        self.populate_playlist_ui()
        if not self.is_playing and self.current_track_index == -1:
            self.current_track_index = 0
            self.update_track_info()

    def populate_playlist_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for i, track in enumerate(self.playlist):
            filename = os.path.basename(track)
            btn = ctk.CTkButton(
                self.scrollable_frame, text=f"  {filename}", anchor="w",
                fg_color="transparent", text_color="white",
                hover_color="#333333", command=lambda i=i: self.select_track(i)
            )
            btn.pack(fill="x", pady=2)

    def update_track_info(self):
        if self.current_track_index != -1:
            path = self.playlist[self.current_track_index]
            try:
                audio = EasyMP3(path)
                title = audio.get('title', [os.path.basename(path)])[0]
                artist = audio.get('artist', ['Unknown Artist'])[0]
                self.track_label.configure(text=title[:40])
                self.artist_label.configure(text=f"{artist} | {title}")
            except:
                filename = os.path.basename(path)
                self.track_label.configure(text=filename[:40])
                self.artist_label.configure(text="Unknown Artist")

    def select_track(self, index):
        self.current_track_index = index
        self.update_track_info()
        if not self.is_playing:
            self.play_music()
        else:
            pygame.mixer.music.load(self.playlist[index])
            pygame.mixer.music.play()

    def play_music(self):
        if self.current_track_index != -1:
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            pygame.mixer.music.play()
            time.sleep(0.1)
            self.is_playing = True
            self.btn_play.configure(text="⏸", fg_color="#eab308")

    def toggle_play(self):
        if not self.is_playing and self.current_track_index != -1:
            self.play_music()
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶", fg_color="#3b82f6")

    def next_track(self):
        if self.current_track_index != -1:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
            self.update_track_info()
            self.play_music()
            self.btn_play.configure(text="⏸", fg_color="#eab308")

    def prev_track(self):
        if self.current_track_index != -1:
            self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
            self.update_track_info()
            self.play_music()
            self.btn_play.configure(text="⏸", fg_color="#eab308")

    def remove_current(self):
        if self.current_track_index != -1:
            self.playlist.pop(self.current_track_index)
            if self.current_track_index >= len(self.playlist):
                self.current_track_index = len(self.playlist) - 1
            self.populate_playlist_ui()
            if self.current_track_index != -1:
                self.update_track_info()
                if self.is_playing:
                    self.play_music()
            else:
                self.track_label.configure(text="No Track Selected")
                self.artist_label.configure(text="Select a song to start")
                self.btn_play.configure(text="▶", fg_color="#3b82f6")

    def clear_all(self):
        self.playlist = []
        self.current_track_index = -1
        self.populate_playlist_ui()
        self.track_label.configure(text="No Track Selected")
        self.artist_label.configure(text="Select a song to start")
        self.progress_bar.set(0)
        self.btn_play.configure(text="▶", fg_color="#3b82f6")

    def set_volume(self, value):
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)

    def update_engine(self):
        while True:
            time.sleep(1)
            if self.is_playing and self.current_track_index != -1:
                try:
                    track_path = self.playlist[self.current_track_index]
                    audio_info = MP3(track_path)
                    duration = audio_info.info.length
                    current_pos = pygame.mixer.music.get_pos() / 1000.0
                    if duration > 0:
                        progress = current_pos / duration
                        self.progress_bar.set(min(progress, 1.0))
                    if not pygame.mixer.music.get_busy() or current_pos >= duration:
                        self.next_track()
                except:
                    pass
            else:
                self.progress_bar.set(0)

if __name__ == "__main__":
    app = MusicPlayer()
    app.btn_add_files.configure(command=app.add_files)
    app.btn_add_folder.configure(command=app.add_folder)
    app.btn_remove_current.configure(command=app.remove_current)
    app.btn_clear_all.configure(command=app.clear_all)
    app.mainloop()