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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NovaCAynE Player By: JethroTeK")
        self.geometry("1100x750")
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass
        # --- Auto-Cleanup Logic ---
        self.clear_previous_downloads()
        pygame.mixer.init()
        self.client_id = "1542393465311338606"
        self.rpc = None
        try:
            self.rpc = pypresence.Presence(self.client_id)
            self.rpc.connect()
            print("Discord RPC initialized successfully.")
        except Exception as e:
            print(f"Discord RPC failed to initialize: {e}")
            self.rpc = None
        self.playlist = []
        self.current_track_index = -1
        self.is_playing = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)
        self.update_thread = threading.Thread(target=self.update_engine, daemon=True)
        self.update_thread.start()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.playlist_frame = ctk.CTkFrame(self, width=350, fg_color="#1a1a1a")
        self.playlist_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.logo_img = None
        try:
            img_path = resource_path("logo.png")
            self.logo_img = ctk.CTkImage(light_image=Image.open(img_path),
                                         dark_image=Image.open(img_path),
                                         size=(150, 150))
        except Exception as e:
            print(f"Notice: Logo image not found or failed to load: {e}")
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
        # Buttons Section
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
        self.btn_yt_link = ctk.CTkButton(
            self.playlist_frame,
            text="Add from YouTube (Link)",
            fg_color="#9333ea",
            hover_color="#7e22ce",
            font=("Arial", 13, "bold"),
            height=35
        )
        self.btn_yt_link.pack(side="bottom", pady=(0, 5), padx=20)
        self.btn_yt_search = ctk.CTkButton(
            self.playlist_frame,
            text="Search by Artist/Track",
            fg_color="#9333ea",
            hover_color="#7e22ce",
            font=("Arial", 13, "bold"),
            height=35
        )
        self.btn_yt_search.pack(side="bottom", pady=(0, 5), padx=20)
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

        # Progress bar area
        self.status_label = ctk.CTkLabel(self.player_frame, text="", font=("Arial", 14), text_color="#3b82f6")
        self.status_label.pack(pady=(0, 0))

        # CHANGED: Replaced progress_bar with a CTkSlider for "Seek" functionality
        self.progress_slider = ctk.CTkSlider(self.player_frame, from_=0, to=1, width=500, progress_color="#3b82f6")
        self.progress_slider.set(0)
        self.progress_slider.configure(command=self.seek_track)
        self.progress_slider.pack(pady=10)

        self.controls_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.controls_frame.pack(pady=30)
        
        # Rewind (Skip Back 15s)
        self.btn_rewind = ctk.CTkButton(
            self.controls_frame, text="⏪", width=60, height=60,
            font=("Arial", 30), fg_color="#2d2d2d", hover_color="#3d3d3d",
            command=self.rewind_track
        )
        self.btn_rewind.grid(row=0, column=0, padx=5)
        
        self.btn_prev = ctk.CTkButton(
            self.controls_frame, text="⏮", width=60, height=60,
            font=("Arial", 30), fg_color="#2d2d2d", hover_color="#3d3d3d",
            command=self.prev_track
        )
        self.btn_prev.grid(row=0, column=1, padx=10)
        self.btn_play = ctk.CTkButton(
            self.controls_frame, text="▶", width=100, height=60,
            font=("Arial", 30, "bold"), fg_color="#3b82f6",
            command=self.toggle_play
        )
        self.btn_play.grid(row=0, column=2, padx=10)
        self.btn_next = ctk.CTkButton(
            self.controls_frame, text="⏭", width=60, height=60,
            font=("Arial", 30), fg_color="#2d2d2d", hover_color="#3d3d3d",
            command=self.next_track
        )
        self.btn_next.grid(row=0, column=3, padx=5)

        # Fast Forward (Skip Forward 15s)
        self.btn_fast_forward = ctk.CTkButton(
            self.controls_frame, text="⏩", width=60, height=60,
            font=("Arial", 30), fg_color="#2d2d2d", hover_color="#3d3d3d",
            command=self.fast_forward_track
        )
        self.btn_fast_forward.grid(row=0, column=4, padx=5)

        self.volume_slider = ctk.CTkSlider(self.player_frame, from_=0, to=1, width=400, command=self.set_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(pady=20)

    # --- Logic for Seek / Skip ---
    def seek_track(self, value):
        """Forces a seek by reloading the track at the specific timestamp."""
        if self.current_track_index != -1:
            try:
                track_path = self.playlist[self.current_track_index]
                audio_info = MP3(track_path)
                duration = audio_info.info.length
                new_pos = value * duration
                
                # We reload the track and immediately start it at the new position
                # This prevents the "reset to start" bug entirely.
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play(start=new_pos)
            except Exception as e:
                print(f"Seek Error: {e}")

    def fast_forward_track(self):
        """Skips forward 15 seconds."""
        if self.current_track_index != -1:
            current_pos = pygame.mixer.music.get_pos()
            pygame.mixer.music.play(start=current_pos + 15)

    def rewind_track(self):
        """Skips backward 15 seconds."""
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
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
            except:
                pass
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                progress_percent = float(p_str) / 100
                self.status_label.configure(text=f"Downloading: {p_str}%")
                self.progress_slider.set(progress_percent)
            except:
                pass
    def download_yt(self, source):
        ydl_opts = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'default_search': 'ytsearch',
            'progress_hooks': [self.progress_hook],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        try:
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.status_label.configure(text="Searching/Initializing...", text_color="#3b82f6")
                info_dict = ydl.extract_info(source, download=True)
                if 'entries' in info_dict:
                    info_dict = info_dict['entries'][0]
                raw_path = ydl.prepare_filename(info_dict)
                if not raw_path.lower().endswith(".mp3"):
                    return os.path.splitext(raw_path)[0] + ".mp3"
                return raw_path
        except Exception as e:
            print(f"YT Download Error: {e}")
            return None
        finally:
            self.status_label.configure(text="", text_color="#3b82f6")
            self.progress_slider.set(0)
    def add_yt_link(self):
        from tkinter import simpledialog
        url = simpledialog.askstring("Input", "Paste YouTube URL:")
        if url:
            def thread_task():
                path = self.download_yt(url)
                if path:
                    self.update_playlist([path])
            threading.Thread(target=thread_task, daemon=True).start()
    def add_yt_search(self):
        from tkinter import simpledialog
        artist = simpledialog.askstring("Input", "Enter Artist Name:")
        track = simpledialog.askstring("Input", "Enter Track Name:")
        if artist and track:
            query = f"{artist} {track}"
            def thread_task():
                path = self.download_yt(query)
                if path:
                    self.update_playlist([path])
                else:
                    messagebox.showerror("Error", "Failed to find/download via search.")
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
                self.rpc.update(
                    state=f"By: {artist_name}"[:128],
                    details=f"Listening to {track_title}"[:128],
                    large_image="playing",
                    large_text="NovaCAynE Player"
                )
            except Exception as e:
                print(f"Discord Update Failed: {e}")
    def add_files(self):
        files = filedialog.askopenfilenames(title="Select MP3 Files", filetypes=[("MP3 Files", "*.mp3")])
        if files:
            self.update_playlist(list(files))
    def add_folder(self):
        path = filedialog.askdirectory(title="Select Music Folder")
        if path:
            files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(".mp3")]
            if files:
                self.update_playlist(files)
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
                fg_color="transparent", text_color="white",
                hover_color="#333333", command=lambda i=i: self.select_track(i)
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
        self.progress_slider.set(0)
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
                        self.progress_slider.set(min(progress, 1.0))
                    if not pygame.mixer.music.get_busy() or current_pos >= duration:
                        self.next_track()
                except Exception:
                    pass
            else:
                self.progress_slider.set(0)

if __name__ == "__main__":
    app = MusicPlayer()
    app.btn_yt_link.configure(command=app.add_yt_link)
    app.btn_yt_search.configure(command=app.add_yt_search)
    if len(sys.argv) > 1:
        file_arg = sys.argv[1]
        if file_arg.lower().endswith(".mp3"):
            app.playlist = [file_arg]
            app.current_track_index = 0
            app.update_track_info()
            app.populate_playlist_ui()
            app.play_music()
    app.btn_add_files.configure(command=app.add_files)
    app.btn_add_folder.configure(command=app.add_folder)
    app.btn_remove_current.configure(command=app.remove_current)
    app.btn_clear_all.configure(command=app.clear_all)
    app.mainloop()
    app.mainloop()