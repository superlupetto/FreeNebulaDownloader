import os
import sys
import threading
import subprocess
import urllib.request
import zipfile
import shutil
from tkinter import *
from tkinter import ttk, messagebox

# =====================
# VERSION
# =====================
VERSION = "2.1"
BASE_URL = "https://raw.githubusercontent.com/superlupetto/FreeSuperDownloader/main/"
VERSION_URL = BASE_URL + "version.txt"
# GitHub raw URLs are case-sensitive: keep filename exact
UPDATE_URL = BASE_URL + "FreeSuperDownloader.exe"

# =====================
# PATHS
# =====================
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "FreeSuperDownloader")
MUSIC_DIR = os.path.join(BASE_DIR, "Musica")
VIDEO_DIR = os.path.join(BASE_DIR, "Video")
FFMPEG_DIR = os.path.join(BASE_DIR, "ffmpeg")
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "bin", "ffmpeg.exe")

os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# =====================
# yt-dlp
# =====================
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

# =====================
# LOG
# =====================
def log(msg):
    try:
        output.configure(state="normal")
        output.insert(END, msg + "\n")
        output.see(END)
        output.configure(state="disabled")
    except:
        print(msg)

# =====================
# FFmpeg
# =====================
def check_ffmpeg():
    return (
        os.path.exists(os.path.join(FFMPEG_DIR, "bin", "ffmpeg.exe")) and
        os.path.exists(os.path.join(FFMPEG_DIR, "bin", "ffprobe.exe"))
    )


def install_ffmpeg():
    if check_ffmpeg():
        return

    log("Installazione FFmpeg (auto repair mode)...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(BASE_DIR, "ffmpeg.zip")

    try:
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(BASE_DIR)

        # move correct folder
        for f in os.listdir(BASE_DIR):
            if "ffmpeg" in f.lower():
                src = os.path.join(BASE_DIR, f)
                if os.path.isdir(src):
                    # ensure clean install
                    if os.path.exists(FFMPEG_DIR):
                        shutil.rmtree(FFMPEG_DIR, ignore_errors=True)
                    shutil.move(src, FFMPEG_DIR)
                    break

        os.remove(zip_path)

        if check_ffmpeg():
            log("FFmpeg OK (auto-repair completato)")
        else:
            log("FFmpeg installato ma ffprobe mancante")

    except Exception as e:
        log(str(e))


def check_update():
    try:
        # version.txt may be missing; fall back to parsing VERSION from the remote script
        data = urllib.request.urlopen(UPDATE_URL, timeout=8).read().decode(errors="ignore")
        remote = None
        for line in data.splitlines():
            line = line.strip()
            if line.startswith("VERSION") and "=" in line:
                # expected: VERSION = "2.1"
                try:
                    remote = line.split("=", 1)[1].strip().strip("'\"")
                except Exception:
                    remote = None
                break
        if not remote:
            return False, None
        return remote != VERSION, remote
    except:
        return False, None


def run_update():
    try:
        log("Aggiornamento in corso...")
        new_file = os.path.join(BASE_DIR, "update.py")
        urllib.request.urlretrieve(UPDATE_URL, new_file)

        bat = os.path.join(BASE_DIR, "update.bat")
        exe = sys.argv[0]

        with open(bat, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 >nul\n")
            f.write(f"move /y \"{new_file}\" \"{exe}\"\n")
            f.write(f"start python \"{exe}\"\n")
            f.write("del %0\n")

        subprocess.Popen(bat, shell=True)
        root.destroy()

    except Exception as e:
        log(str(e))

# =====================
# YT-DLP UPDATE
# =====================
def update_ytdlp():
    try:
        log("Aggiornamento yt-dlp...")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "yt-dlp"
        ])
        log("yt-dlp aggiornato")
    except Exception as e:
        log(str(e))

# =====================
# DOWNLOAD CORE
# =====================
progress_var = None
progress_bar = None
mode = None
url_entry = None
output = None


# toast notification

def toast(msg):
    t = Toplevel(root)
    t.overrideredirect(True)
    t.configure(bg="#ffffff")
    t.geometry(f"260x60+{root.winfo_x()+30}+{root.winfo_y()+30}")
    Frame(t, bg="#e2e8f0", height=1).pack(fill=X, side=TOP)
    Frame(t, bg="#e2e8f0", height=1).pack(fill=X, side=BOTTOM)
    Label(t, text=msg, bg="#ffffff", fg="#0f172a", font=("Segoe UI", 10)).pack(expand=True)
    t.after(1600, t.destroy)


def progress_hook(d):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '').strip()
        progress_var.set(p)
        try:
            val = float(p.replace('%',''))
            progress_bar['value'] = val
        except:
            pass
    elif d['status'] == 'finished':
        progress_var.set("100%")
        progress_bar['value'] = 100
        try:
            # UI updates must run on the Tk main thread
            root.after(0, lambda: (url_entry.delete(0, END) if url_entry else None))
        except Exception:
            pass
        toast("Download completato")


def download_thread(url):
    try:
        install_ffmpeg()

        opts = {
            'outtmpl': os.path.join(MUSIC_DIR if mode.get() == 'mp3' else VIDEO_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'ffmpeg_location': os.path.join(FFMPEG_DIR, "bin"),
            'quiet': True,
            'no_warnings': True,
        }

        if mode.get() == 'mp3':
            # MP3 TURBO STABLE MODE (no ffprobe dependency issues)
            opts.update({
                'format': 'bestaudio/best',
                'ffmpeg_location': os.path.join(FFMPEG_DIR, "bin"),
                'outtmpl': os.path.join(MUSIC_DIR, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'keepvideo': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
                # extra safety flags
                'prefer_ffmpeg': True,
                'postprocessor_args': ['-vn']
            })
        else:
            q = quality.get() if 'quality' in globals() else 'best'

            if q == 'best':
                # Prefer MP4 container + H.264 (avc1) + AAC (m4a) to avoid Opus incompatibility
                fmt = 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                fmt = f"bestvideo[height<={q}][vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={q}][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"

            opts['format'] = fmt
            opts['merge_output_format'] = 'mp4'
            opts['format_sort'] = ['res', 'fps', 'codec:h264', 'acodec:aac', 'ext:mp4:m4a']
            # Force AAC audio if Opus is selected by fallback; keep video stream when possible.
            opts['postprocessor_args'] = ['-movflags', '+faststart', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        log("Download completato")

    except Exception as e:
        log(str(e))


# =====================
# DOWNLOAD QUEUE SYSTEM (PRO)
# =====================

download_queue = []
queue_running = False


def process_queue():
    global queue_running
    queue_running = True

    while download_queue:
        url = download_queue.pop(0)
        try:
            log(f"In coda: {url}")
            install_ffmpeg()

            opts = {
                'outtmpl': os.path.join(MUSIC_DIR if mode.get() == 'mp3' else VIDEO_DIR, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [progress_hook],
                'ffmpeg_location': os.path.join(FFMPEG_DIR, "bin"),
                'quiet': True,
                'no_warnings': True,
            }

            if mode.get() == 'mp3':
                opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'
                    }]
                })
            else:
                q = quality.get() if 'quality' in globals() else 'best'
                if q == 'best':
                    fmt = 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    fmt = f"bestvideo[height<={q}][vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={q}][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"

                opts['format'] = fmt
                opts['merge_output_format'] = 'mp4'
                opts['format_sort'] = ['res', 'fps', 'codec:h264', 'acodec:aac', 'ext:mp4:m4a']
                opts['postprocessor_args'] = ['-movflags', '+faststart', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            log("Download completato")

        except Exception as e:
            log(str(e))

    queue_running = False
    toast("Coda completata")


def download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Errore", "Inserisci link")
        return

    download_queue.append(url)
    toast("Aggiunto in coda")

    global queue_running
    if not queue_running:
        threading.Thread(target=process_queue, daemon=True).start()


# =====================
# OPEN
# =====================
def open_folder(p):
    os.startfile(p)


# =====================
# DRAG & DROP PASTE SUPPORT
# =====================
def paste_url(event):
    try:
        url_entry.delete(0, END)
        url_entry.insert(0, root.clipboard_get())
    except:
        pass


# =====================
# UI MODERNA DEFINITIVA (GLASS + SPACIOUS)
# =====================

root = Tk()
root.title("FreeSuperDownloader PRO")
root.geometry("820x650")
root.configure(bg="#f6f7fb")
root.attributes('-alpha', 0.0)

# fade in

def fade(i=0):
    if i < 1:
        root.attributes('-alpha', i)
        root.after(15, lambda: fade(i+0.05))

def _rounded_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
    # Tkinter Canvas has no native rounded rectangle; build it from primitives.
    r = max(0, min(r, int((x2 - x1) / 2), int((y2 - y1) / 2)))
    items = []
    items.append(canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs))
    items.append(canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs))
    items.append(canvas.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, **kwargs))
    items.append(canvas.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, **kwargs))
    items.append(canvas.create_oval(x1, y2 - 2 * r, x1 + 2 * r, y2, **kwargs))
    items.append(canvas.create_oval(x2 - 2 * r, y2 - 2 * r, x2, y2, **kwargs))
    return items

class AnimatedModeToggle(Frame):
    def __init__(self, master, variable, on_value="mp3", off_value="mp4", width=180, height=38, **kwargs):
        super().__init__(master, bg=kwargs.pop("bg", "#ffffff"))
        self.variable = variable
        self.on_value = on_value
        self.off_value = off_value
        self.w = width
        self.h = height

        self.canvas = Canvas(self, width=self.w, height=self.h, bg=self["bg"], highlightthickness=0)
        self.canvas.pack()

        self.pad = 4
        self.knob_size = self.h - 2 * self.pad
        self.left_x = self.pad
        self.right_x = self.w - self.pad - self.knob_size
        self._knob_x = self.left_x
        self._anim_id = None

        self._bg_items = []
        self._knob_item = None
        self._txt_left = None
        self._txt_right = None

        self._render()
        self.canvas.bind("<Button-1>", self._on_click)
        self.variable.trace_add("write", lambda *_: self._sync(animated=True))
        self._sync(animated=False)

    def _is_on(self):
        return self.variable.get() == self.on_value

    def _target_x(self):
        return self.left_x if self._is_on() else self.right_x

    def _colors(self):
        if self._is_on():
            return ("#22c55e", "#0f172a")  # track, inner-dot
        return ("#6366f1", "#0f172a")

    def _render(self):
        self.canvas.delete("all")
        track_color, text_bg = self._colors()

        self._bg_items = _rounded_rect(
            self.canvas,
            0 + 1, 0 + 1, self.w - 1, self.h - 1,
            r=int(self.h / 2),
            fill=track_color,
            outline="#e2e8f0",
            width=1
        )

        # Labels (inside track)
        self._txt_left = self.canvas.create_text(
            self.w * 0.30, self.h / 2,
            text="🎵 MP3",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )
        self._txt_right = self.canvas.create_text(
            self.w * 0.70, self.h / 2,
            text="🎬 MP4",
            fill="white",
            font=("Segoe UI", 10, "bold")
        )

        # Knob
        x = self._knob_x
        y = self.pad
        self._knob_item = self.canvas.create_oval(
            x, y, x + self.knob_size, y + self.knob_size,
            fill="#ffffff",
            outline="#e2e8f0",
            width=1
        )
        # subtle inner dot
        dot_pad = 10
        self.canvas.create_oval(
            x + dot_pad, y + dot_pad,
            x + self.knob_size - dot_pad, y + self.knob_size - dot_pad,
            fill=text_bg,
            outline=""
        )

    def _set_track_color(self):
        track_color, _ = self._colors()
        for item in self._bg_items:
            self.canvas.itemconfigure(item, fill=track_color)

    def _on_click(self, event):
        # Click left/right half sets mode deterministically; click on knob toggles.
        if event.x < self.w / 2:
            self.variable.set(self.on_value)
        elif event.x > self.w / 2:
            self.variable.set(self.off_value)
        else:
            self.variable.set(self.off_value if self._is_on() else self.on_value)

    def _sync(self, animated=True):
        self._set_track_color()
        target = self._target_x()
        if not animated:
            self._knob_x = target
            self._render()
            return
        self._animate_to(target)

    def _animate_to(self, target_x):
        if self._anim_id is not None:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

        # lazy render if missing
        if self._knob_item is None:
            self._render()

        # Smooth easing
        dx = target_x - self._knob_x
        if abs(dx) < 1:
            self._knob_x = target_x
            self._render()
            return

        step = dx / 6.0
        self._knob_x += step
        self._render()
        self._anim_id = self.after(15, lambda: self._animate_to(target_x))

# =====================
# LIGHT FUTURE THEME (UI/UX ONLY)
# =====================
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure("TProgressbar", thickness=10, troughcolor="#e2e8f0", background="#6366f1")

style.configure("Primary.TButton",
                font=("Segoe UI", 10, "bold"),
                padding=(18, 10),
                background="#111827",
                foreground="#ffffff",
                borderwidth=0)
style.map("Primary.TButton",
          background=[("active", "#0b1220"), ("pressed", "#0b1220")])

style.configure("Secondary.TButton",
                font=("Segoe UI", 10),
                padding=(16, 10),
                background="#ffffff",
                foreground="#0f172a",
                borderwidth=1,
                relief="flat")
style.map("Secondary.TButton",
          background=[("active", "#f1f5f9"), ("pressed", "#f1f5f9")])

style.configure("Chip.TButton",
                font=("Segoe UI", 9),
                padding=(12, 8),
                background="#f1f5f9",
                foreground="#0f172a",
                borderwidth=0)
style.map("Chip.TButton",
          background=[("active", "#e2e8f0"), ("pressed", "#e2e8f0")])

container = Frame(root, bg="#f6f7fb")
container.pack(expand=True, fill=BOTH, padx=52, pady=40)

# HEADER
header = Frame(container, bg="#f6f7fb")
header.pack(fill=X)

Label(header, text="FreeSuperDownloader", font=("Segoe UI", 24, "bold"), bg="#f6f7fb", fg="#0f172a").pack(anchor="w")
Label(header, text="Downloader & Convert • minimal future UI",
      font=("Segoe UI", 10), bg="#f6f7fb", fg="#64748b").pack(anchor="w", pady=(6, 0))

version = Label(header, text="v3.1", bg="#f6f7fb", fg="#64748b", font=("Segoe UI", 9))
version.place(relx=1.0, x=-10, y=5, anchor="ne")

# CARD
card = Frame(container, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
card.pack(fill=BOTH, expand=True, pady=22)

mode = StringVar(value="mp3")

# animated toggle (MP3 / MP4)
mode_frame = Frame(card, bg="#ffffff")
mode_frame.pack(pady=(22, 12))

AnimatedModeToggle(mode_frame, variable=mode, width=220, height=42, bg="#ffffff").pack()
progress_var = StringVar(value="0%")

Label(card, text="Incolla un link", bg="#ffffff", fg="#0f172a",
      font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=26, pady=(14, 6))

url_entry = Entry(card, bg="#f1f5f9", fg="#0f172a", insertbackground="#0f172a",
                  relief="flat", highlightthickness=1, highlightbackground="#e2e8f0", highlightcolor="#6366f1")
url_entry.pack(fill=X, padx=26, ipady=10, pady=(0, 8))

# RIGHT CLICK PASTE MENU (modern UX)
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Incolla", command=lambda: url_entry.event_generate("<<Paste>>"))
context_menu.add_command(label="Incolla e avvia", command=lambda: (url_entry.event_generate("<<Paste>>"), download()))


def show_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

url_entry.bind("<Button-3>", show_menu)
url_entry.bind("<Control-v>", lambda e: None)
url_entry.bind("<Double-Button-1>", paste_url)

btns = Frame(card, bg="#ffffff")
btns.pack(pady=(14, 10))

ttk.Button(btns, text="Download", command=download, style="Primary.TButton").pack(side=LEFT, padx=6)
ttk.Button(btns, text="Update", command=run_update, style="Secondary.TButton").pack(side=LEFT, padx=6)
ttk.Button(btns, text="yt-dlp", command=update_ytdlp, style="Secondary.TButton").pack(side=LEFT, padx=6)

folder = Frame(card, bg="#ffffff")
folder.pack(pady=(0, 8))

ttk.Button(folder, text="Apri Musica", command=lambda: open_folder(MUSIC_DIR), style="Chip.TButton").pack(side=LEFT, padx=6)
ttk.Button(folder, text="Apri Video", command=lambda: open_folder(VIDEO_DIR), style="Chip.TButton").pack(side=LEFT, padx=6)

# progress LIVE CARD
progress_bar = ttk.Progressbar(card, mode='determinate', length=520, style="TProgressbar")
progress_bar.pack(pady=(16, 8))

Label(card, textvariable=progress_var, bg="#ffffff", fg="#64748b", font=("Segoe UI", 9)).pack()

output = Text(card, height=10, bg="#f8fafc", fg="#0f172a",
              insertbackground="#0f172a", relief="flat",
              highlightthickness=1, highlightbackground="#e2e8f0", highlightcolor="#6366f1")
output.pack(fill=BOTH, padx=26, pady=(16, 24))

fade()
root.mainloop()
