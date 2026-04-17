import os
import sys
import threading
import subprocess
import urllib.request
import zipfile
import shutil
from tkinter import *
from tkinter import ttk, messagebox, filedialog

# =====================
# VERSION
# =====================
VERSION = "2.1"
BASE_URL = "https://raw.githubusercontent.com/superlupetto/FreeSuperDownloader/main/"
VERSION_URL = BASE_URL + "version.txt"
UPDATE_CANDIDATES = [
    "FreeSuperDownloader.exe",
    "FreeSuperDownloader.pyw",
    "FreeSuperDownloader.py",
]

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
        remote = None
        try:
            remote = urllib.request.urlopen(VERSION_URL, timeout=8).read().decode(errors="ignore").strip()
        except Exception:
            remote = None

        # version.txt may be missing; fall back to parsing VERSION from a remote script.
        if not remote:
            script_url = _resolve_update_url(prefer_scripts=True)
            if script_url:
                data = urllib.request.urlopen(script_url, timeout=8).read().decode(errors="ignore")
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


def _resolve_update_url(prefer_scripts=False):
    candidates = UPDATE_CANDIDATES[:]
    if prefer_scripts:
        candidates = [c for c in candidates if c.endswith((".py", ".pyw"))] + [c for c in candidates if c.endswith(".exe")]
    for filename in candidates:
        url = BASE_URL + filename
        try:
            with urllib.request.urlopen(url, timeout=8):
                return url
        except Exception:
            continue
    return None


def run_update():
    try:
        log("Aggiornamento in corso...")
        update_url = _resolve_update_url()
        if not update_url:
            raise Exception("Update non disponibile: file remoto non trovato (404).")

        remote_ext = os.path.splitext(update_url)[1] or ".tmp"
        new_file = os.path.join(BASE_DIR, f"update{remote_ext}")
        urllib.request.urlretrieve(update_url, new_file)

        bat = os.path.join(BASE_DIR, "update.bat")
        app_path = sys.argv[0]

        with open(bat, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 >nul\n")
            f.write(f"move /y \"{new_file}\" \"{app_path}\"\n")
            if app_path.lower().endswith(".exe"):
                f.write(f"start \"\" \"{app_path}\"\n")
            else:
                f.write(f"start \"\" python \"{app_path}\"\n")
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


def _is_unavailable_format_error(err):
    msg = str(err).lower()
    return "requested format is not available" in msg


def _is_auth_required_error(err):
    msg = str(err).lower()
    return (
        "requiring login" in msg
        or "authentication" in msg
        or "--cookies-from-browser" in msg
        or "--cookies" in msg
        or "sign in" in msg
    )


def _try_with_browser_cookies(url, opts):
    # Try common browsers on Windows. This helps with TikTok and other gated content.
    browsers = ("chrome", "edge", "firefox")
    last_err = None
    for browser in browsers:
        retry_opts = dict(opts)
        retry_opts["cookiesfrombrowser"] = (browser,)
        try:
            log(f"Contenuto protetto: provo cookie browser ({browser})...")
            with yt_dlp.YoutubeDL(retry_opts) as ydl:
                ydl.download([url])
            log(f"Accesso autenticato riuscito con cookie: {browser}")
            return True
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    return False


def _try_with_cookies_file(url, opts):
    # Auto-detect exported cookies file in common app locations.
    candidates = [
        os.path.join(BASE_DIR, "cookies.txt"),
        os.path.join(os.path.dirname(sys.argv[0]), "cookies.txt"),
        os.path.join(os.getcwd(), "cookies.txt"),
    ]
    seen = set()
    found_any_cookie_file = False
    for cookie_path in candidates:
        cookie_path = os.path.abspath(cookie_path)
        if cookie_path in seen:
            continue
        seen.add(cookie_path)
        if not os.path.exists(cookie_path):
            continue
        found_any_cookie_file = True

        retry_opts = dict(opts)
        retry_opts["cookiefile"] = cookie_path
        try:
            log(f"Contenuto protetto: provo file cookie ({cookie_path})...")
            with yt_dlp.YoutubeDL(retry_opts) as ydl:
                ydl.download([url])
            log("Accesso autenticato riuscito con cookies.txt")
            return True
        except Exception:
            continue
    if not found_any_cookie_file:
        log("cookies.txt non trovato. Percorsi controllati:")
        for p in seen:
            log(f" - {p}")
    return False


def _download_with_fallback(url, opts, current_mode):
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        return
    except Exception as e:
        if _is_auth_required_error(e):
            try:
                if _try_with_browser_cookies(url, opts):
                    return
            except Exception:
                pass
            try:
                if _try_with_cookies_file(url, opts):
                    return
            except Exception:
                pass
            raise Exception(
                "Questo contenuto richiede login. Apri TikTok nel browser, effettua l'accesso e riprova. "
                "Se continua a fallire, esporta i cookie in un file cookies.txt e mettilo in Documents\\FreeSuperDownloader."
            )

        if not _is_unavailable_format_error(e):
            raise

        log("Formato richiesto non disponibile: riprovo con fallback compatibile...")
        retry_opts = dict(opts)
        if current_mode == 'mp3':
            retry_opts['format'] = 'bestaudio/best'
        else:
            # Generic fallback for sites like Pinterest where strict format filters can fail.
            retry_opts['format'] = 'best/bestvideo+bestaudio'
            retry_opts.pop('format_sort', None)
            retry_opts['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(retry_opts) as ydl:
            ydl.download([url])


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

        _download_with_fallback(url, opts, mode.get())

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

            _download_with_fallback(url, opts, mode.get())

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

#
# =====================
# LOCAL FILE TOOLS (MKV->MP4 / Extract MP3)
# =====================
local_files = []
local_files_list = None


def _safe_filename(s: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        s = s.replace(ch, "_")
    return s.strip().strip(".")


def choose_local_files():
    global local_files
    paths = filedialog.askopenfilenames(
        title="Seleziona file multimediali",
        filetypes=[
            ("Media", "*.mkv *.mp4 *.webm *.mov *.avi *.m4v *.flv *.mp3 *.m4a *.aac *.wav *.ogg *.opus"),
            ("Tutti i file", "*.*"),
        ],
    )
    if not paths:
        return
    local_files = list(paths)
    if local_files_list is not None:
        local_files_list.delete(0, END)
        for p in local_files:
            local_files_list.insert(END, p)
    toast(f"Selezionati {len(local_files)} file")


def clear_local_files():
    global local_files
    local_files = []
    if local_files_list is not None:
        local_files_list.delete(0, END)


def _ffmpeg_run(args):
    install_ffmpeg()
    exe = os.path.join(FFMPEG_DIR, "bin", "ffmpeg.exe")
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def _convert_one_mkv_to_mp4(src_path: str):
    base = os.path.splitext(os.path.basename(src_path))[0]
    base = _safe_filename(base) or "video"
    dst_path = os.path.join(VIDEO_DIR, base + ".mp4")

    # Fast path: stream copy to MP4 (works when codecs are MP4-compatible).
    r = _ffmpeg_run(["-i", src_path, "-map", "0", "-c", "copy", "-movflags", "+faststart", dst_path])
    if r.returncode == 0:
        return dst_path, None

    # Fallback: re-encode to H.264 + AAC for maximum compatibility.
    r2 = _ffmpeg_run([
        "-i", src_path,
        "-map", "0:v:0?", "-map", "0:a:0?", "-map", "0:s:0?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-c:s", "mov_text",
        "-movflags", "+faststart",
        dst_path
    ])
    if r2.returncode == 0:
        return dst_path, None
    return None, (r2.stderr or r.stderr or "Errore FFmpeg")


def _extract_mp3_from_video(src_path: str):
    base = os.path.splitext(os.path.basename(src_path))[0]
    base = _safe_filename(base) or "audio"
    dst_path = os.path.join(MUSIC_DIR, base + ".mp3")

    r = _ffmpeg_run([
        "-i", src_path,
        "-vn",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        dst_path
    ])
    if r.returncode == 0:
        return dst_path, None
    return None, (r.stderr or "Errore FFmpeg")


def _run_local_batch(kind: str):
    if not local_files:
        messagebox.showerror("Errore", "Seleziona almeno un file")
        return

    def worker():
        try:
            total = len(local_files)
            for i, p in enumerate(list(local_files), start=1):
                try:
                    progress_bar['value'] = 0
                except Exception:
                    pass
                progress_var.set(f"{i}/{total}")
                log(f"{'Converti' if kind=='mkv2mp4' else 'Estrai MP3'}: {p}")

                if kind == "mkv2mp4":
                    out, err = _convert_one_mkv_to_mp4(p)
                else:
                    out, err = _extract_mp3_from_video(p)

                if out:
                    log(f"OK -> {out}")
                    try:
                        progress_bar['value'] = 100
                    except Exception:
                        pass
                else:
                    log(f"ERRORE -> {err}")

            toast("Operazione completata")
        except Exception as e:
            log(str(e))

    threading.Thread(target=worker, daemon=True).start()


def convert_mkv_to_mp4():
    _run_local_batch("mkv2mp4")


def extract_mp3_local():
    _run_local_batch("extractmp3")


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
root.geometry("820x920")
root.configure(bg="#f2f4ff")
root.minsize(780, 860)
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

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _blend(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex((_lerp(r1, r2, t), _lerp(g1, g2, t), _lerp(b1, b2, t)))


def _draw_glow_blob(canvas, cx, cy, r, color, steps=18):
    # Simulate a soft glow by drawing multiple transparent-ish rings (Tk has no alpha).
    # We approximate by blending towards background.
    bg = "#f2f4ff"
    for i in range(steps):
        t = i / max(1, steps - 1)
        # Softer / more subtle (closer to background)
        col = _blend(color, bg, 0.70 + t * 0.25)
        rr = int(r * (1 - t * 0.85))
        canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, fill=col, outline="")


class GlassCard(Frame):
    def __init__(self, master, radius=22, **kwargs):
        super().__init__(master, bg=kwargs.pop("bg", "#000000"))
        self.radius = radius

        self.canvas = Canvas(self, bg=self["bg"], highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)

        self.content = Frame(self.canvas, bg="#ffffff")
        self._win = self.canvas.create_window(0, 0, window=self.content, anchor="nw")

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, _e=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return
        self.canvas.delete("glass")

        # Frosted base
        base = "#ffffff"
        edge = "#dbe2ff"
        _rounded_rect(self.canvas, 1, 1, w - 1, h - 1, r=self.radius, fill=base, outline=edge, width=1, tags="glass")

        # Top highlight band (liquid/glass feel) – avoid arc artifacts
        highlight_h = int(h * 0.28)
        _rounded_rect(
            self.canvas,
            6, 6, w - 6, max(20, highlight_h),
            r=max(10, self.radius - 6),
            fill="#f7f8ff",
            outline="",
            tags="glass"
        )
        # Subtle inner border
        _rounded_rect(self.canvas, 4, 4, w - 4, h - 4, r=self.radius - 3, fill="", outline="#f8fafc", width=1, tags="glass")

        # place inner content with padding
        pad = 18
        self.canvas.coords(self._win, pad, pad)
        self.canvas.itemconfigure(self._win, width=w - pad * 2, height=h - pad * 2)


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
            return ("#e8fff1", "#16a34a")  # track, accent
        return ("#eef2ff", "#4f46e5")

    def _render(self):
        self.canvas.delete("all")
        track_color, accent = self._colors()

        self._bg_items = _rounded_rect(
            self.canvas,
            0 + 1, 0 + 1, self.w - 1, self.h - 1,
            r=int(self.h / 2),
            fill=track_color,
            outline="#dbe2ff",
            width=1
        )

        # inner highlight
        _rounded_rect(
            self.canvas,
            2, 2, self.w - 2, int(self.h / 2),
            r=int(self.h / 2),
            fill="#ffffff",
            outline="",
        )

        # Labels (inside track)
        self._txt_left = self.canvas.create_text(
            self.w * 0.30, self.h / 2,
            text="MP3",
            fill="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        self._txt_right = self.canvas.create_text(
            self.w * 0.70, self.h / 2,
            text="MP4",
            fill="#0f172a",
            font=("Segoe UI", 10, "bold")
        )

        # Knob
        x = self._knob_x
        y = self.pad
        # soft shadow
        self.canvas.create_oval(
            x + 2, y + 3, x + self.knob_size + 2, y + self.knob_size + 3,
            fill="#e9edff",
            outline="",
        )
        self._knob_item = self.canvas.create_oval(
            x, y, x + self.knob_size, y + self.knob_size,
            fill="#ffffff",
            outline="#dbe2ff",
            width=1
        )
        # subtle inner dot
        dot_pad = 10
        self.canvas.create_oval(
            x + dot_pad, y + dot_pad,
            x + self.knob_size - dot_pad, y + self.knob_size - dot_pad,
            fill=accent,
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
# LIQUID GLASS THEME (UI/UX ONLY)
# =====================
style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure("TProgressbar", thickness=10, troughcolor="#e7eaff", background="#4f46e5")

style.configure("Primary.TButton",
                font=("Segoe UI", 10, "bold"),
                padding=(18, 11),
                background="#0f172a",
                foreground="#ffffff",
                borderwidth=0,
                relief="flat")
style.map("Primary.TButton",
          background=[("active", "#111b3d"), ("pressed", "#111b3d")])

style.configure("Secondary.TButton",
                font=("Segoe UI", 10),
                padding=(16, 11),
                background="#ffffff",
                foreground="#0f172a",
                borderwidth=1,
                relief="flat")
style.map("Secondary.TButton",
          background=[("active", "#f7f8ff"), ("pressed", "#f7f8ff")])

style.configure("Chip.TButton",
                font=("Segoe UI", 9),
                padding=(12, 9),
                background="#f1f3ff",
                foreground="#0f172a",
                borderwidth=0)
style.map("Chip.TButton",
          background=[("active", "#e7eaff"), ("pressed", "#e7eaff")])

# Background canvas (liquid blobs)
bg = Canvas(root, bg="#f2f4ff", highlightthickness=0)
bg.pack(fill=BOTH, expand=True)

container = Frame(bg, bg="#f2f4ff")
container.place(relx=0.5, rely=0.5, anchor="center")
container.pack_propagate(False)

def _layout_bg(_e=None):
    w = root.winfo_width()
    h = root.winfo_height()
    bg.delete("blob")
    # soft blobs
    scale = min(w, h)
    _draw_glow_blob(bg, int(w * 0.14), int(h * 0.22), int(scale * 0.20), "#a5b4fc", steps=14)
    _draw_glow_blob(bg, int(w * 0.92), int(h * 0.18), int(scale * 0.16), "#c4b5fd", steps=14)
    _draw_glow_blob(bg, int(w * 0.76), int(h * 0.74), int(scale * 0.22), "#93c5fd", steps=14)
    _draw_glow_blob(bg, int(w * 0.18), int(h * 0.82), int(scale * 0.14), "#a7f3d0", steps=14)
    # keep container centered and sized
    max_w = min(980, w - 56)
    max_h = min(980, h - 46)
    container.configure(width=max_w, height=max_h)
    container.place_configure(relx=0.5, rely=0.5, anchor="center", width=max_w, height=max_h)

root.bind("<Configure>", _layout_bg)

# HEADER
header = Frame(container, bg="#f2f4ff")
header.pack(fill=X, padx=12, pady=(8, 10))

Label(header, text="FreeSuperDownloader", font=("Segoe UI", 24, "bold"), bg="#f2f4ff", fg="#0f172a").pack(anchor="w")
Label(header, text="Downloader & Convert • minimal future UI",
      font=("Segoe UI", 10), bg="#f2f4ff", fg="#64748b").pack(anchor="w", pady=(6, 0))

version = Label(header, text="v3.1", bg="#f2f4ff", fg="#64748b", font=("Segoe UI", 9))
version.place(relx=1.0, x=-10, y=5, anchor="ne")

# CARD
card = GlassCard(container, radius=26, bg="#f2f4ff")
card.pack(fill=BOTH, expand=True, padx=12, pady=(0, 14))
card_body = card.content

mode = StringVar(value="mp3")

# animated toggle (MP3 / MP4)
mode_frame = Frame(card_body, bg="#ffffff")
mode_frame.pack(pady=(6, 12))

AnimatedModeToggle(mode_frame, variable=mode, width=280, height=44, bg="#ffffff").pack()
progress_var = StringVar(value="0%")

Label(card_body, text="Incolla un link", bg="#ffffff", fg="#0f172a",
      font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6, 6))

url_entry = Entry(card_body, bg="#f7f8ff", fg="#0f172a", insertbackground="#0f172a",
                  relief="flat", highlightthickness=1, highlightbackground="#dbe2ff", highlightcolor="#4f46e5")
url_entry.pack(fill=X, ipady=12, pady=(0, 10))

# RIGHT CLICK PASTE MENU (modern UX)
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Incolla", command=lambda: url_entry.event_generate("<<Paste>>"))
context_menu.add_command(label="Incolla e avvia", command=lambda: (url_entry.event_generate("<<Paste>>"), download()))


def show_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

url_entry.bind("<Button-3>", show_menu)
url_entry.bind("<Control-v>", lambda e: None)
url_entry.bind("<Double-Button-1>", paste_url)

btns = Frame(card_body, bg="#ffffff")
btns.pack(pady=(14, 10))

ttk.Button(btns, text="Download", command=download, style="Primary.TButton").pack(side=LEFT, padx=6)
ttk.Button(btns, text="Update", command=run_update, style="Secondary.TButton").pack(side=LEFT, padx=6)
ttk.Button(btns, text="yt-dlp", command=update_ytdlp, style="Secondary.TButton").pack(side=LEFT, padx=6)

folder = Frame(card_body, bg="#ffffff")
folder.pack(pady=(0, 8))

ttk.Button(folder, text="Apri Musica", command=lambda: open_folder(MUSIC_DIR), style="Chip.TButton").pack(side=LEFT, padx=6)
ttk.Button(folder, text="Apri Video", command=lambda: open_folder(VIDEO_DIR), style="Chip.TButton").pack(side=LEFT, padx=6)

# progress LIVE CARD
progress_bar = ttk.Progressbar(card_body, mode='determinate', length=560, style="TProgressbar")
progress_bar.pack(pady=(16, 8))

Label(card_body, textvariable=progress_var, bg="#ffffff", fg="#64748b", font=("Segoe UI", 9)).pack()

output = Text(card_body, height=10, bg="#fbfcff", fg="#0f172a",
              insertbackground="#0f172a", relief="flat",
              highlightthickness=1, highlightbackground="#dbe2ff", highlightcolor="#4f46e5")
output.pack(fill=BOTH, pady=(16, 6))

# LOCAL FILES CARD (liquid glass)
local_card = GlassCard(container, radius=26, bg="#f2f4ff")
local_card.pack(fill=BOTH, expand=False, padx=12, pady=(0, 10))
local_body = local_card.content

Label(local_body, text="File locali", bg="#ffffff", fg="#0f172a",
      font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6, 10))

local_actions = Frame(local_body, bg="#ffffff")
local_actions.pack(fill=X)

ttk.Button(local_actions, text="Seleziona file…", command=choose_local_files, style="Secondary.TButton").pack(side=LEFT, padx=(0, 8))
ttk.Button(local_actions, text="Pulisci", command=clear_local_files, style="Chip.TButton").pack(side=LEFT)

ttk.Button(local_actions, text="Converti MKV → MP4", command=convert_mkv_to_mp4, style="Primary.TButton").pack(side=RIGHT, padx=(8, 0))
ttk.Button(local_actions, text="Estrai MP3", command=extract_mp3_local, style="Secondary.TButton").pack(side=RIGHT)

local_list_frame = Frame(local_body, bg="#ffffff")
local_list_frame.pack(fill=BOTH, pady=(12, 6))

local_files_list = Listbox(local_list_frame, height=4, bg="#fbfcff", fg="#0f172a",
                           highlightthickness=1, highlightbackground="#dbe2ff", relief="flat",
                           selectbackground="#dbe2ff", selectforeground="#0f172a")
local_files_list.pack(fill=BOTH, expand=True)

fade()
root.mainloop()
