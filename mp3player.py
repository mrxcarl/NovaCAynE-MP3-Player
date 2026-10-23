import os
import sys
import threading
import time
import pygame
import customtkinter as ctk
from tkinter import filedialog, messagebox
from mutagen.mp3 import MP3
from mutagen.mp3 import EasyMP3
from PIL import Image
import pypresence
import yt_dlp

# --- Configuration & Styling ---
COLORS = {
    "bg_dark": "#0f0f1a",        # Deep Midnight
    "bg_panel": "#16162a",       # Slightly lighter for depth
    "accent_blue": "#3b82f6",    # Primary Blue
    "accent_purple": "#9333ea",  # Secondary Purple
    "accent_red": "#dc2626",     # Danger/Clear
    "text_main": "#ffffff",
    "text_dim": "#a1a1aa",
    "border": "#2d2d4d"
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("Dark")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NovaCAynE Player")
        self.geometry("1100x750")
        
        # Setup Colors
        self.configure(fg_color=COLORS["bg_dark"])

        try:
            self.iconbitmap(resource_path("icon.ico"))
        except:
            pass

        # --- Logic Initialization ---
        self.clear_previous_downloads()
        pygame.mixer.init()
        self.client_id = "1542393465311338606"
        self.rpc = None
        try:
            self.rpc = pypresence.Presence(self.client_id)
            self.rpc.connect()
        except:
            self.rpc = None

        self.playlist = []
        self.current_track_index = -1
        self.is_playing = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)

        self.update_thread = threading.Thread(target=self.update_engine, daemon=True)
        self.update_thread.start()

        # --- UI Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar (Library)
        self.playlist_frame = ctk.CTkFrame(
            self, width=350, fg_color=COLORS["bg_panel"], 
            border_color=COLORS["border"], border_width=1, corner_radius=0
        )
        self.playlist_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Sidebar Header
        self.title_label = ctk.CTkLabel(
            self.playlist_frame, text="LIBRARY", 
            font=("Orbitron", 24, "bold"), text_color=COLORS["accent_blue"]
        )
        self.title_label.pack(pady=(30, 10))

        # Logo Area
        try:
            img_path = resource_path("logo.png")
            self.logo_img = ctk.CTkImage(Image.open(img_path), size=(240, 120))
            self.logo_label = ctk.CTkLabel(self.playlist_frame, image=self.logo_img, text="")
            self.logo_label.pack(pady=10)
        except:
            pass

        # Scrollable Area
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.playlist_frame, fg_color="transparent", 
            label_text="QUEUE", label_text_color=COLORS["text_dim"]
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sidebar Action Buttons
        self.btn_frame = ctk.CTkFrame(self.playlist_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=10)

        # Styling for consistent buttons
        btn_style = {"font": ("Arial", 12, "bold"), "height": 35, "corner_radius": 8}
        
        self.btn_add_files = ctk.CTkButton(self.btn_frame, text="Add Files", fg_color=COLORS["accent_blue"], 
                                             hover_color="#2563eb", **btn_style)
        self.btn_add_files.pack(fill="x", pady=2)
        
        self.btn_add_folder = ctk.CTkButton(self.btn_frame, text="Add Folder", fg_color=COLORS["accent_blue"], 
                                              hover_color="#2563eb", **btn_style)
        self.btn_add_folder.pack(fill="x", pady=2)

        self.btn_yt_link = ctk.CTkButton(self.btn_frame, text="YouTube Link", fg_color=COLORS["accent_purple"], 
                                          hover_color="#7e22ce", **btn_style)
        self.btn_yt_link.pack(fill="x", pady=2)

        self.btn_yt_search = ctk.CTkButton(self.btn_frame, text="Search Artist", fg_color=COLORS["accent_purple"], 
                                             hover_color="#7e22ce", **btn_style)
        self.btn_yt_search.pack(fill="x", pady=2)

        self.btn_remove_current = ctk.CTkButton(self.btn_frame, text="Remove Current", fg_color="#eab308", 
                                                  hover_color="#ca8a04", **btn_style)
        self.btn_remove_current.pack(fill="x", pady=2)

        self.btn_clear_all = ctk.CTkButton(self.btn_frame, text="Clear All", fg_color=COLORS["accent_red"], 
                                             hover_color="#b91c1c", **btn_style)
        self.btn_clear_all.pack(fill="x", pady=10)

        # Main Player Area
        self.player_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], border_color=COLORS["border"], border_width=1)
        self.player_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        # Center Content
        self.track_label = ctk.CTkLabel(
            self.player_frame, text="No Track Selected",
            font=("Arial", 42, "bold"), text_color=COLORS["text_main"]
        )
        self.track_label.pack(pady=(120, 10))

        self.artist_label = ctk.CTkLabel(
            self.player_frame, text="Select a song to start",
            font=("Arial", 18), text_color=COLORS["text_dim"]
        )
        self.artist_label.pack(pady=(0, 50))

        # Progress Section
        self.status_label = ctk.CTkLabel(self.player_frame, text="", font=("Arial", 12), text_color=COLORS["accent_blue"])
        self.status_label.pack()

        self.progress_slider = ctk.CTkSlider(
            self.player_frame, from_=0, to=1, width=600, 
            progress_color=COLORS["accent_blue"], fg_color=COLORS["border"]
        )
        self.progress_slider.set(0)
        self.progress_slider.configure(command=self.seek_track)
        self.progress_slider.pack(pady=10)

        # Control Panel
        self.controls_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.controls_frame.pack(pady=30)

        # Control Buttons Styling
        ctrl_btn = {"width": 60, "height": 60, "font": ("Arial", 30), "fg_color": "#1e1e3a", "hover_color": "#2a2a5a", "corner_radius": 30} 
        
        self.btn_rewind = ctk.CTkButton(self.controls_frame, text="⏪", **ctrl_btn, command=self.rewind_track)
        self.btn_rewind.grid(row=0, column=0, padx=10)
        
        self.btn_prev = ctk.CTkButton(self.controls_frame, text="⏮", **ctrl_btn, command=self.prev_track)
        self.btn_prev.grid(row=0, column=1, padx=10)

        self.btn_play = ctk.CTkButton(
            self.controls_frame, text="▶", width=100, height=60,
            font=("Arial", 35, "bold"), fg_color=COLORS["accent_blue"], 
            hover_color="#2563eb", corner_radius=30, command=self.toggle_play
        )
        self.btn_play.grid(row=0, column=2, padx=10)

        self.btn_next = ctk.CTkButton(self.controls_frame, text="⏭", **ctrl_btn, command=self.next_track)
        self.btn_next.grid(row=0, column=3, padx=10)

        self.btn_fast_forward = ctk.CTkButton(self.controls_frame, text="⏩", **ctrl_btn, command=self.fast_forward_track)
        self.btn_fast_forward.grid(row=0, column=4, padx=10)

        # Volume Slider
        self.volume_slider = ctk.CTkSlider(
            self.player_frame, from_=0, to=1, width=400, 
            progress_color=COLORS["accent_purple"], fg_color=COLORS["border"]
        )
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(pady=20)
        
        # Volume Icon/Label
        vol_label = ctk.CTkLabel(self.player_frame, text="VOLUME", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"])
        vol_label.pack()

    # --- Logic Methods (Stay same as your original code) ---
    def seek_track(self, value):
        if self.current_track_index != -1:
            try:
                track_path = self.playlist[self.current_track_index]
                audio_info = MP3(track_path)
                duration = audio_info.info.length
                new_pos = value * duration
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play(start=new_pos)
            except Exception as e:
                print(f"Seek Error: {e}")

    def fast_forward_track(self):
        if self.current_track_index != -1:
            current_pos = pygame.mixer.music.get_pos()
            pygame.mixer.music.play(start=current_pos + 15)

    def rewind_track(self):
        if self.current_track_index != -1:
            current_pos = pygame.mixer.music.get_pos()
            new_pos = max(0, current_pos - 15)
            pygame.mixer.music.play(start=new_pos)

    def clear_previous_downloads(self):
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        for f in os.listdir("downloads"):
            path = os.path.join("downloads", f)
            try:
                if os.path.isfile(path): os.remove(path)
                elif os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
            except: pass

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                progress_percent = float(p_str) / 100
                self.status_label.configure(text=f"Downloading: {p_str}%", text_color=COLORS["accent_blue"])
                self.progress_slider.set(progress_percent)
            except: pass

    def download_yt(self, source):
        ydl_opts = {
            'format': 'bestaudio',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True, 'no_warnings': True, 'noplaylist': True,
            'default_search': 'ytsearch',
            'progress_hooks': [self.progress_hook],
            'http_headers': {'User-Agent': 'Mozilla/5.0'}
        }
        try:
            if not os.path.exists("downloads"): os.makedirs("downloads")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.status_label.configure(text="Searching...", text_color=COLORS["accent_blue"])
                info_dict = ydl.extract_info(source, download=True)
                if 'entries' in info_dict: info_dict = info_dict['entries'][0]
                raw_path = ydl.prepare_filename(info_dict)
                if not raw_path.lower().endswith(".mp3"):
                    return os.path.splitext(raw_path)[0] + ".mp3"
                return raw_path
        except Exception as e:
            print(f"YT Download Error: {e}")
            return None
        finally:
            self.status_label.configure(text="", text_color=COLORS["accent_blue"])
            self.progress_slider.set(0)

    def add_yt_link(self):
        from tkinter import simpledialog
        url = simpledialog.askstring("Input", "Paste YouTube URL:")
        if url:
            def thread_task():
                path = self.download_yt(url)
                if path: self.update_playlist([path])
            threading.Thread(target=thread_task, daemon=True).start()

    def add_yt_search(self):
        from tkinter import simpledialog
        artist = simpledialog.askstring("Input", "Enter Artist Name:")
        track = simpledialog.askstring("Input", "Enter Track Name:")
        if artist and track:
            query = f"{artist} {track}"
            def thread_task():
                path = self.download_yt(query)
                if path: self.update_playlist([path])
                else: messagebox.showerror("Error", "Failed to find track.")
            threading.Thread(target=thread_task, daemon=True).start()

    def update_track_info(self):
        track_title = "No Track Selected"
        artist_name = "Unknown Artist"
        if self.current_track_index != -1:
            path = self.playlist[self.current_track_index]
            try:
                audio = EasyMP3(path)
                track_title = audio.get('title', [os.path.basename(path)])[0]
                artist_name = audio.get('artist', ['Unknown Artist'])[0]
            except Exception:
                track_title = os.path.basename(path)
        self.track_label.configure(text=track_title[:40])
        self.artist_label.configure(text=f"{artist_name} | {track_title}")
        if self.rpc:
            try:
                self.rpc.update(state=f"By: {artist_name}", details=f"Listening to {track_title}")
            except: pass

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select MP3 Files", filetypes=[("MP3 Files", "*.mp3")])
        if files: self.update_playlist(list(files))

    def add_folder(self):
        path = filedialog.askdirectory(title="Select Music Folder")
        if path:
            files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(".mp3")]
            if files: self.update_playlist(files)

    def update_playlist(self, new_files):
        self.playlist.extend(new_files)
        self.playlist = list(set(self.playlist))
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
                fg_color="transparent", text_color=COLORS["text_main"],
                hover_color=COLORS["bg_panel"],
                command=lambda i=i: self.select_track(i)
            )
            btn.pack(fill="x", pady=2)

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
            self.btn_play.configure(text="⏸", fg_color=COLORS["accent_red"])

    def toggle_play(self):
        if not self.is_playing and self.current_track_index != -1:
            self.play_music()
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶", fg_color=COLORS["accent_blue"])

    def next_track(self):
        if self.current_track_index != -1:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
            self.update_track_info()
            self.play_music()
            self.btn_play.configure(text="⏸", fg_color=COLORS["accent_red"])

    def prev_track(self):
        if self.current_track_index != -1:
            self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
            self.update_track_info()
            self.play_music()
            self.btn_play.configure(text="⏸", fg_color=COLORS["accent_red"])

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
                self.btn_play.configure(text="▶", fg_color=COLORS["accent_blue"])

    def clear_all(self):
        self.playlist = []
        self.current_track_index = -1
        self.populate_playlist_ui()
        self.track_label.configure(text="No Track Selected")
        self.artist_label.configure(text="Select a song to start")
        self.progress_slider.set(0)
        self.btn_play.configure(text="▶", fg_color=COLORS["accent_blue"])

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
                        self.progress_slider.set(min(progress, 1.0))
                    if not pygame.mixer.music.get_busy() or current_pos >= duration:
                        self.next_track()
                except:
                    pass
            else:
                self.progress_slider.set(0)

if __name__ == "__main__":
    app = MusicPlayer()
    app.btn_yt_link.configure(command=app.add_yt_link)
    app.btn_yt_search.configure(command=app.add_yt_search)
    app.btn_add_files.configure(command=app.add_files)
    app.btn_add_folder.configure(command=app.add_folder)
    app.btn_remove_current.configure(command=app.remove_current)
    app.btn_clear_all.configure(command=app.clear_all)
    
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        if file_arg.lower().endswith(".mp3"):
            app.playlist = [file_arg]
            app.current_track_index = 0
            app.update_track_info()
            app.populate_playlist_ui()
            app.play_music()
            
    app.mainloop()