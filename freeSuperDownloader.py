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
VERSION = "2.2"
BASE_URL = "https://raw.githubusercontent.com/superlupetto/FreeSuperDownloader/main/"
VERSION_URL = BASE_URL + "version.txt"
UPDATE_URL = BASE_URL + "freeSuperDownloader.py"

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
def install_ffmpeg():
    if os.path.exists(FFMPEG_PATH):
        return

    log("Installazione FFmpeg...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(BASE_DIR, "ffmpeg.zip")

    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(BASE_DIR)

    for f in os.listdir(BASE_DIR):
        if "ffmpeg" in f.lower():
            src = os.path.join(BASE_DIR, f)
            if os.path.isdir(src):
                shutil.move(src, FFMPEG_DIR)
                break

    os.remove(zip_path)
    log("FFmpeg pronto")

# =====================
# UPDATE SYSTEM
# =====================
def check_update():
    try:
        remote = urllib.request.urlopen(VERSION_URL, timeout=5).read().decode().strip()
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
    t.configure(bg="#111827")
    t.geometry(f"260x60+{root.winfo_x()+30}+{root.winfo_y()+30}")
    Label(t, text=msg, bg="#111827", fg="white", font=("Segoe UI", 10)).pack(expand=True)
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
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        else:
            q = quality.get() if 'quality' in globals() else 'best'

            if q == 'best':
                fmt = 'bv*+ba/b'
            else:
                fmt = f"bestvideo[height<={q}]+bestaudio/best"

            opts['format'] = fmt
            opts['merge_output_format'] = 'mp4'
            opts['format_sort'] = ['res', 'fps', 'codec:h264', 'ext:mp4:m4a']
            opts['postprocessor_args'] = ['-movflags', '+faststart']

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        log("Download completato")

    except Exception as e:
        log(str(e))


def download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Errore", "Inserisci link")
        return

    toast("Download avviato")
    progress_bar['value'] = 0
    threading.Thread(target=download_thread, args=(url,), daemon=True).start()

    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Errore", "Inserisci link")
        return

    toast("Download avviato")
    progress_bar['value'] = 0
    threading.Thread(target=download_thread, args=(url,), daemon=True).start()


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
root.configure(bg="#0b1220")
root.attributes('-alpha', 0.0)

# fade in

def fade(i=0):
    if i < 1:
        root.attributes('-alpha', i)
        root.after(15, lambda: fade(i+0.05))

container = Frame(root, bg="#0b1220")
container.pack(expand=True, fill=BOTH, padx=40, pady=30)

# HEADER
header = Frame(container, bg="#0b1220")
header.pack(fill=X)

# mac controls
c = Canvas(header, width=80, height=20, bg="#0b1220", highlightthickness=0)
c.pack(side=LEFT)
c.create_oval(5,5,15,15,fill="#ff5f57",outline="")
c.create_oval(25,5,35,15,fill="#ffbd2e",outline="")
c.create_oval(45,5,55,15,fill="#28c840",outline="")

Label(header, text="FreeSuperDownloader", font=("Segoe UI", 22, "bold"), bg="#0b1220", fg="white").pack()

version = Label(header, text="v2.2", bg="#0b1220", fg="#94a3b8", font=("Segoe UI", 9))
version.place(relx=1.0, x=-10, y=5, anchor="ne")

# CARD
card = Frame(container, bg="#111827")
card.pack(fill=BOTH, expand=True, pady=20)

mode = StringVar(value="mp3")

# segmented control (icons MP3 / MP4)
mode_frame = Frame(card, bg="#111827")
mode_frame.pack(pady=10)

mp3_btn = Button(mode_frame, text="🎵 MP3", width=12,
                 bg="#22c55e", fg="white", relief="flat",
                 command=lambda: mode.set("mp3"))
mp3_btn.pack(side=LEFT, padx=6)

mp4_btn = Button(mode_frame, text="🎬 MP4", width=12,
                 bg="#1f2937", fg="white", relief="flat",
                 command=lambda: mode.set("mp4"))
mp4_btn.pack(side=LEFT, padx=6)
progress_var = StringVar(value="0%")

Label(card, text="URL", bg="#111827", fg="white").pack(anchor="w", padx=20, pady=(20,5))

url_entry = Entry(card, bg="#1f2937", fg="white", insertbackground="white", relief="flat")
url_entry.pack(fill=X, padx=20, ipady=8)
url_entry.bind("<Double-Button-1>", paste_url)

btns = Frame(card, bg="#111827")
btns.pack(pady=15)

Button(btns, text="Download", command=download).pack(side=LEFT, padx=5)
Button(btns, text="Update", command=run_update).pack(side=LEFT, padx=5)
Button(btns, text="yt-dlp", command=update_ytdlp).pack(side=LEFT, padx=5)

folder = Frame(card, bg="#111827")
folder.pack()

Button(folder, text="Musica", command=lambda: open_folder(MUSIC_DIR)).pack(side=LEFT, padx=5)
Button(folder, text="Video", command=lambda: open_folder(VIDEO_DIR)).pack(side=LEFT, padx=5)

# progress LIVE CARD
progress_bar = ttk.Progressbar(card, mode='determinate', length=400)
progress_bar.pack(pady=20)

Label(card, textvariable=progress_var, bg="#111827", fg="#94a3b8").pack()

output = Text(card, height=10, bg="#0a0f1c", fg="#93c5fd", insertbackground="white")
output.pack(fill=BOTH, padx=20, pady=20)

fade()
root.mainloop()
