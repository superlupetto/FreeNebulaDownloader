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
VERSION = "1.0"
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
# LOG (unchanged)
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
# FFmpeg (unchanged)
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
# UPDATE SYSTEM (unchanged)
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
# YT-DLP UPDATE (unchanged)
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
# DOWNLOAD (UNCHANGED)
# =====================
def progress_hook(d):
    if d['status'] == 'downloading':
        progress_var.set(d.get('_percent_str', '').strip())
    elif d['status'] == 'finished':
        progress_var.set("100%")


def download_thread(url):
    try:
        install_ffmpeg()

        opts = {
            'outtmpl': os.path.join(MUSIC_DIR if mode.get() == 'mp3' else VIDEO_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'restrictfilenames': True,
            'progress_hooks': [progress_hook],
            'ffmpeg_location': os.path.join(FFMPEG_DIR, "bin"),
        }

        if mode.get() == 'mp3':
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        else:
            opts['format'] = 'best[ext=mp4]'

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
    threading.Thread(target=download_thread, args=(url,), daemon=True).start()

# =====================
# OPEN
# =====================
def open_folder(p):
    os.startfile(p)

# =====================
# UI MODERNA LIQUID GLASS (MINIMAL + SPACIOUS)
# =====================
root = Tk()
root.title("FreeSuperDownloader PRO")
root.geometry("760x600")
root.configure(bg="#f4f7ff")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=10)
style.configure("TLabel", font=("Segoe UI", 10), background="#f4f7ff")

mode = StringVar(value="mp3")
progress_var = StringVar(value="Pronto")

# MAIN WRAPPER (floating glass feel)
container = Frame(root, bg="#f4f7ff")
container.pack(expand=True, fill=BOTH, padx=40, pady=30)

# HEADER
header = Frame(container, bg="#f4f7ff")
header.pack(fill=X, pady=(0,20))

Label(header, text="FreeSuperDownloader", font=("Segoe UI", 22, "bold"), bg="#f4f7ff", fg="#1b2b4a").pack()
Label(header, text="minimal • modern • liquid UI", font=("Segoe UI", 11), bg="#f4f7ff", fg="#6b7a99").pack()

# CARD
card = Frame(container, bg="#ffffff")
card.pack(fill=BOTH, expand=True)

# spacing helper
pad = 18

Label(card, text="Video URL", bg="#ffffff", fg="#1b2b4a", font=("Segoe UI", 11)).pack(anchor="w", padx=pad, pady=(pad,5))

url_entry = Entry(card, font=("Segoe UI", 12), bg="#f3f6ff", relief="flat", bd=0)
url_entry.pack(fill=X, padx=pad, ipady=10)

# MODE
mode_frame = Frame(card, bg="#ffffff")
mode_frame.pack(pady=20)

Radiobutton(mode_frame, text="Audio MP3", variable=mode, value="mp3", bg="#ffffff", indicatoron=0, padx=18, pady=8).pack(side=LEFT, padx=10)
Radiobutton(mode_frame, text="Video MP4", variable=mode, value="mp4", bg="#ffffff", indicatoron=0, padx=18, pady=8).pack(side=LEFT, padx=10)

# BUTTONS (pill-like feel)
btn_frame = Frame(card, bg="#ffffff")
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Download").pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Update App", command=run_update).pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Update yt-dlp", command=update_ytdlp).pack(side=LEFT, padx=6)

# FOLDERS
folder_frame = Frame(card, bg="#ffffff")
folder_frame.pack(pady=10)

ttk.Button(folder_frame, text="Musica", command=lambda: open_folder(MUSIC_DIR)).pack(side=LEFT, padx=6)
ttk.Button(folder_frame, text="Video", command=lambda: open_folder(VIDEO_DIR)).pack(side=LEFT, padx=6)

# PROGRESS
Label(card, textvariable=progress_var, bg="#ffffff", fg="#334a6b", font=("Segoe UI", 11)).pack(pady=10)

# LOG (soft glass dark)
output = Text(card, height=10, bg="#0b1220", fg="#d6e4ff", relief="flat", insertbackground="white")
output.pack(fill=BOTH, padx=pad, pady=(10,pad))
output.configure(state="disabled")

root.mainloop()
