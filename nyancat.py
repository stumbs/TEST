# ╔══════════════════════════════════════════════════════════╗
# ║        FINAL SELF-DELETING NYAN CAT SCRIPT               ║
# ╚══════════════════════════════════════════════════════════╝

import os, sys, tempfile, shutil, threading, time, subprocess, urllib.request
import tkinter as tk
from PIL import Image, ImageTk

# --- Configuration ---
# These now point to GitHub RAW links instead of local C:/ paths
ORIGINAL_GIF = "https://raw.githubusercontent.com/YOURNAME/YOURREPO/main/nyancat.gif"
ORIGINAL_MP3 = "https://raw.githubusercontent.com/YOURNAME/YOURREPO/main/nyanloop.mp3"

# ─── Self-Destruct Function (External Cleanup) ─────────────────────
def start_self_destruct(exe_path):
    """
    Creates and launches a separate, detached batch script (cleanup.bat) 
    to delete the executable after a short delay (when the main process has released the file lock).
    """
    # Only proceed if the script is compiled into an executable
    if not getattr(sys, 'frozen', False):
        return

    # Create a unique batch file path to avoid conflicts
    bat = os.path.join(tempfile.gettempdir(), f"cleanup_{os.getpid()}.bat")
    
    with open(bat, "w") as f:
        f.write('@echo off\n')
        # Wait 1 second to ensure the main EXE has fully closed and released the lock
        f.write('timeout /t 1 /nobreak >nul\n') 
        # Attempt to delete the executable
        f.write(f'del /F /Q "{exe_path}" >nul 2>&1\n')
        # Delete the batch file itself
        f.write(f'del /F /Q "%~f0"\n')
        
    # Launch the batch file in a separate, detached CMD process
    subprocess.Popen(
        f'cmd /c "{bat}"',
        creationflags=subprocess.CREATE_NO_WINDOW
    )

# ─── MAIN NYAN CAT CLASS ─────────────────────────────────────────────
class NyanCatApp:
    def __init__(self, root):
        self.root = root
        self.exe_path = sys.executable # Store the path to the running executable

        root.title("Document Viewer")
        root.configure(bg="black")
        root.geometry("800x600")
        root.resizable(False, False)
        
        # Bind the window closure (X button, ESC key, or root.destroy()) to the on_exit handler
        root.bind("<Escape>", lambda e: self.on_exit())
        root.protocol("WM_DELETE_WINDOW", self.on_exit) 

        # Cache folder
        self.cache = os.path.join(tempfile.gettempdir(), ".__data_cache__")
        os.makedirs(self.cache, exist_ok=True)

        # NEW: download GIF/MP3 into temp with same renamed filenames
        self.gif_path = os.path.join(self.cache, "config.bin")
        self.mp3_path = os.path.join(self.cache, "cache.dat")

        urllib.request.urlretrieve(ORIGINAL_GIF, self.gif_path)
        urllib.request.urlretrieve(ORIGINAL_MP3, self.mp3_path)

        # UI
        self.label = tk.Label(root, bg="black", bd=0, highlightthickness=0)
        self.label.pack(expand=True)

        # Load GIF frames
        self.frames = []
        self.load_frames()

        # Start animation and sound
        threading.Thread(target=self.play_sound, daemon=True).start()
        self.frame_idx = 0
        self.animate()

    def load_frames(self):
        """Extracts and caches all GIF frames and their specific durations."""
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
            print(f"Error loading GIF frames: {e}")
            
        if not self.frames:
            try:
                img = Image.open(self.gif_path).convert("RGBA")
                photo = ImageTk.PhotoImage(img)
                self.frames.append((photo, 50))
            except:
                pass

    def animate(self):
        """Updates the frame displayed in the window."""
        if not self.frames:
            return

        photo, delay = self.frames[self.frame_idx]
        self.label.config(image=photo)
        self.label.image = photo
        
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.root.after(delay, self.animate)

    def play_sound(self):
        """Loads and loops the MP3 file using pygame."""
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
        """Cleans temp folder and self-deletes the EXE (if compiled)."""
        try:
            shutil.rmtree(self.cache)
        except:
            pass 

        self.root.destroy()
        start_self_destruct(self.exe_path)

# ─── LAUNCH ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Hide console window immediately for stealth
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

    root = tk.Tk()
    app = NyanCatApp(root)
    root.mainloop()
