import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

# --- CONFIGURAZIONE ---
BASE_DIR = r"C:\Super Downloader"
MUSIC_DIR = os.path.join(BASE_DIR, "Musica")
VIDEO_DIR = os.path.join(BASE_DIR, "Video")
FFMPEG_ROOT = r"C:\FFmpeg"
FFMPEG_EXE = os.path.join(FFMPEG_ROOT, "bin", "ffmpeg.exe")
UPDATE_URL = "https://github.com/superlupetto/SuperDownloader/blob/main/SuperDownloader.py"
FF_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
SCRIPT_PATH = os.path.abspath(__file__)

# --- AUTO-INSTALLAZIONE LIBRERIE ---
try:
    import yt_dlp
except ImportError:
    print(">>> Installazione yt-dlp in corso...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

def installa_ffmpeg_auto():
    """Scarica ed estrae FFmpeg BtbN in C:\\FFmpeg se manca"""
    if os.path.exists(FFMPEG_EXE):
        return

    print("\n" + "="*43)
    print("   FFMPEG MANCANTE - INSTALLAZIONE AUTOMATICA")
    print("="*43)
    
    zip_tmp = os.path.join(os.environ.get('TEMP', BASE_DIR), "ffmpeg_btbn.zip")
    temp_extract = r"C:\FFmpeg_Temp_Zip"
    
    try:
        print(f">>> Download da GitHub (BtbN Shared)...")
        req = urllib.request.Request(FF_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_tmp, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        print(">>> Estrazione in corso in C:\\FFmpeg...")
        if os.path.exists(FFMPEG_ROOT): shutil.rmtree(FFMPEG_ROOT)
        if os.path.exists(temp_extract): shutil.rmtree(temp_extract)

        with zipfile.ZipFile(zip_tmp, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)
        
        # Individua la cartella estratta (nome variabile da BtbN)
        extracted_folders = [d for d in os.listdir(temp_extract) if os.path.isdir(os.path.join(temp_extract, d))]
        if extracted_folders:
            shutil.move(os.path.join(temp_extract, extracted_folders[0]), FFMPEG_ROOT)
        
        shutil.rmtree(temp_extract)
        os.remove(zip_tmp)
        print("✅ FFmpeg BtbN installato con successo!")
        print("="*43 + "\n")
    except Exception as e:
        print(f"❌ ERRORE: {e}\n⚠️ Esegui come AMMINISTRATORE!")
        input("Premi Invio per uscire..."); sys.exit()

def inizializza():
    """Crea le cartelle e scarica FFmpeg se necessario"""
    for d in [BASE_DIR, MUSIC_DIR, VIDEO_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    installa_ffmpeg_auto()

def download(url, mode='video'):
    """Gestisce il download tramite yt-dlp"""
    folder = MUSIC_DIR if mode == 'audio' else VIDEO_DIR
    opts = {
        'ffmpeg_location': os.path.join(FFMPEG_ROOT, "bin"),
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best' if mode == 'audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
    }
    
    if mode == 'audio':
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        print(f"\n✅ Download completato in: {folder}")
    except Exception as e:
        print(f"❌ Errore download: {e}")

def update_script():
    print(f"\n[INFO] Controllo aggiornamenti su GitHub...")
    try:
        # User-Agent necessario per non essere bloccati dai server
        req = urllib.request.Request(UPDATE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        temp_file = SCRIPT_PATH + ".new"
        
        with urllib.request.urlopen(req) as response, open(temp_file, 'wb') as out_file:
            out_file.write(response.read())
            
        if os.path.exists(temp_file):
            print(">>> Aggiornamento scaricato. Riavvio in corso...")
            # Crea un file batch temporaneo per sostituire il file in uso
            with open("update.bat", "w") as f:
                f.write(f'''@echo off
timeout /t 1 >nul
move /y "{temp_file}" "{SCRIPT_PATH}"
start python "{SCRIPT_PATH}"
del "%~f0"''')
            subprocess.Popen("update.bat", shell=True)
            sys.exit()
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")
        input("Premi Invio per tornare al menu...")

def main():
    inizializza()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===========================================")
        print("      SUPER DOWNLOADER PRO V1.7")
        print("===========================================")
        print(f" 📂 Path: {BASE_DIR}")
        print("-------------------------------------------")
        print(" [1] -> Scarica MP3 (YouTube)")
        print(" [2] -> Scarica MP4 (YouTube)")
        print(" [3] -> Converti Video Locali in MP3")
        print(" [4] -> AGGIORNA SCRIPT (Server)")
        print(" [5] -> Aggiorna yt-dlp (Libreria)")
        print(" [6] -> Esci")
        print("===========================================")
        
        scelta = input("Scegli: ").strip()
        
        if scelta == '6': break
        elif scelta in ['1', '2']:
            u = input("Incolla Link (o 'x' per tornare): ").strip()
            if u.lower() != 'x' and u:
                download(u, 'audio' if scelta == '1' else 'video')
                input("\nPremi Invio per continuare...")
        elif scelta == '3':
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv', '.webm'))]
            if not files:
                print("Nessun video trovato in cartella Video.")
            for f in files:
                output_name = os.path.splitext(f)[0] + ".mp3"
                print(f"Conversione: {f}...")
                subprocess.run([FFMPEG_EXE, "-i", os.path.join(VIDEO_DIR, f), "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", os.path.join(MUSIC_DIR, output_name), "-y"], capture_output=True)
                print(f"✅ Convertito!")
            input("\nFine elaborazione. Premi Invio...")
        elif scelta == '4':
            update_script()
        elif scelta == '5':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            input("\nLibreria aggiornata! Premi Invio...")

if __name__ == "__main__":
    main()
