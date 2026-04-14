import os
import sys
import threading
import subprocess
import urllib.request
import zipfile
import shutil
from tkinter import *
from tkinter import messagebox

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
# LOG
# =====================
def log(msg):
    try:
        output.insert(END, msg + "\n")
        output.see(END)
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
# YT-DLP UPDATE (AUTO + MANUAL)
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

# auto update at startup (silent)
threading.Thread(target=update_ytdlp, daemon=True).start()

# =====================
# DOWNLOAD
# =====================
def progress_hook(d):
    if d['status'] == 'downloading':
        progress_label.config(text=d.get('_percent_str', '').strip())
    elif d['status'] == 'finished':
        progress_label.config(text="OK")


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
# OPEN FOLDERS
# =====================
def open_folder(p):
    os.startfile(p)

# =====================
# GUI
# =====================
root = Tk()
root.title("FreeSuperDownloader PRO")
root.geometry("540x420")

mode = StringVar(value="mp3")

Label(root, text="Link:").pack()
url_entry = Entry(root, width=60)
url_entry.pack()

Radiobutton(root, text="MP3", variable=mode, value="mp3").pack()
Radiobutton(root, text="MP4", variable=mode, value="mp4").pack()

Button(root, text="Scarica", command=download).pack()
Button(root, text="Aggiorna programma", command=run_update).pack()
Button(root, text="Aggiorna yt-dlp", command=update_ytdlp).pack()

Button(root, text="Musica", command=lambda: open_folder(MUSIC_DIR)).pack()
Button(root, text="Video", command=lambda: open_folder(VIDEO_DIR)).pack()

progress_label = Label(root, text="Pronto")
progress_label.pack()

output = Text(root, height=10)
output.pack(fill=BOTH, expand=True)

root.mainloop()
