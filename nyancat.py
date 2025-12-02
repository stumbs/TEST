# ╔══════════════════════════════════════════════════════════╗
# ║        FINAL SELF-DELETING NYAN CAT SCRIPT               ║
# ╚══════════════════════════════════════════════════════════╝

import os, sys, tempfile, shutil, threading, time, subprocess, urllib.request
import tkinter as tk
from PIL import Image, ImageTk

# --- Configuration ---
# GitHub RAW links
ORIGINAL_GIF = "https://raw.githubusercontent.com/stumbs/TEST/main/nyancat.gif"
ORIGINAL_MP3 = "https://raw.githubusercontent.com/stumbs/TEST/main/nyanloop.mp3"


# --- Reliable downloader (fixes GitHub refusing urlretrieve) ---
def download(url, path):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}  # So GitHub thinks it's a real browser
    )
    with urllib.request.urlopen(req) as r:
        with open(path, "wb") as f:
            f.write(r.read())


# ─── Self-Destruct Function (External Cleanup) ─────────────────────
def start_self_destruct(exe_path):
    if not getattr(sys, 'frozen', False):
        return

    bat = os.path.join(tempfile.gettempdir(), f"cleanup_{os.getpid()}.bat")

    with open(bat, "w") as f:
        f.write('@echo off\n')
        f.write('timeout /t 1 /nobreak >nul\n')
        f.write(f'del /F /Q "{exe_path}" >nul 2>&1\n')
        f.write(f'del /F /Q "%~f0"\n')

    subprocess.Popen(
        f'cmd /c "{bat}"',
        creationflags=subprocess.CREATE_NO_WINDOW
    )


# ─── MAIN NYAN CAT CLASS ─────────────────────────────────────────────
class NyanCatApp:
    def __init__(self, root):
        self.root = root
        self.exe_path = sys.executable

        root.title("Document Viewer")
        root.configure(bg="black")
        root.geometry("800x600")
        root.resizable(False, False)

        root.bind("<Escape>", lambda e: self.on_exit())
        root.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Temp cache
        self.cache = os.path.join(tempfile.gettempdir(), ".__data_cache__")
        os.makedirs(self.cache, exist_ok=True)

        # Renamed hidden temp files
        self.gif_path = os.path.join(self.cache, "config.bin")
        self.mp3_path = os.path.join(self.cache, "cache.dat")

        # Download using fixed function
        download(ORIGINAL_GIF, self.gif_path)
        download(ORIGINAL_MP3, self.mp3_path)

        # UI
        self.label = tk.Label(root, bg="black", bd=0, highlightthickness=0)
        self.label.pack(expand=True)

        # Load frames
        self.frames = []
        self.load_frames()

        threading.Thread(target=self.play_sound, daemon=True).start()
        self.frame_idx = 0
        self.animate()

    def load_frames(self):
        try:
            gif = Image.open(self.gif_path)
            while True:
                frame = gif.copy().convert("RGBA")
                photo = ImageTk.PhotoImage(frame)
                duration = gif.info.get("duration", 50) or 50
                self.frames.append((photo, duration))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"Error loading GIF: {e}")

        if not self.frames:
            try:
                img = Image.open(self.gif_path).convert("RGBA")
                self.frames.append((ImageTk.PhotoImage(img), 50))
            except:
                pass

    def animate(self):
        if not self.frames:
            return

        photo, delay = self.frames[self.frame_idx]
        self.label.config(image=photo)
        self.label.image = photo

        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.root.after(delay, self.animate)

    def play_sound(self):
        time.sleep(0.8)
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(self.mp3_path)
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def on_exit(self):
        try:
            shutil.rmtree(self.cache)
        except:
            pass

        self.root.destroy()
        start_self_destruct(self.exe_path)


# ─── LAUNCH ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

    root = tk.Tk()
    app = NyanCatApp(root)
    root.mainloop()
