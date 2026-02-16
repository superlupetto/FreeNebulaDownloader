import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

# --- CONFIGURAZIONE ---
BASE_DIR = r"C:\Super Downloader"
CONFIG_FILE = os.path.join(BASE_DIR, "config.txt")
MUSIC_DIR = os.path.join(BASE_DIR, "Musica")
VIDEO_DIR = os.path.join(BASE_DIR, "Video")
FFMPEG_ROOT = r"C:\FFmpeg"
FFMPEG_EXE = os.path.join(FFMPEG_ROOT, "bin", "ffmpeg.exe")
UPDATE_URL = "http://lunaremagicafata.duckdns.org/downloads/SuperDownloader.py"
FF_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
SCRIPT_PATH = os.path.abspath(__file__)

LANGS = {
    'it': {'title': "Italiano", 'opt1': "Scarica MP3", 'opt2': "Scarica MP4", 'opt3': "Converti MKV in MP4", 'opt4': "Estrai MP3 da Video Locali", 'opt5': "AGGIORNA SCRIPT", 'opt6': "Aggiorna yt-dlp", 'opt7': "LINGUA", 'opt8': "Esci", 'loop_head': "--- DOWNLOAD CONTINUO (X per uscire) ---", 'loop_prompt': "Link: "},
    'en': {'title': "English", 'opt1': "Download MP3", 'opt2': "Download MP4", 'opt3': "Convert MKV to MP4", 'opt4': "Extract MP3", 'opt5': "UPDATE SCRIPT", 'opt6': "Update yt-dlp", 'opt7': "LANGUAGE", 'opt8': "Exit", 'loop_head': "--- CONTINUOUS DOWNLOAD (X to exit) ---", 'loop_prompt': "Link: "},
    'ja': {'title': "日本語", 'opt1': "MP3ダウンロード", 'opt2': "MP4ダウンロード", 'opt3': "MKV変換", 'opt4': "MP3抽出", 'opt5': "更新", 'opt6': "yt-dlp更新", 'opt7': "言語", 'opt8': "終了", 'loop_head': "--- 連続ダウンロード (Xで戻る) ---", 'loop_prompt': "リンク: "},
    'da': {'title': "Dansk", 'opt1': "Download MP3", 'opt2': "Download MP4", 'opt3': "MKV til MP4", 'opt4': "Ekstraher MP3", 'opt5': "OPDATER", 'opt6': "yt-dlp", 'opt7': "SPROG", 'opt8': "Afslut", 'loop_head': "--- LØBENDE DOWNLOAD (X for menu) ---", 'loop_prompt': "Link: "},
    'fr': {'title': "Français", 'opt1': "Télécharger MP3", 'opt2': "Télécharger MP4", 'opt3': "MKV vers MP4", 'opt4': "Extraire MP3", 'opt5': "MAJ", 'opt6': "yt-dlp", 'opt7': "LANGUE", 'opt8': "Quitter", 'loop_head': "--- TÉLÉCHARGEMENT CONTINU (X pour retour) ---", 'loop_prompt': "Lien: "},
    'hr': {'title': "Hrvatski", 'opt1': "Preuzmi MP3", 'opt2': "Preuzmi MP4", 'opt3': "MKV u MP4", 'opt4': "Ekstrakcija MP3", 'opt5': "AŽURIRAJ", 'opt6': "yt-dlp", 'opt7': "JEZIK", 'opt8': "Izlaz", 'loop_head': "--- KONTINUIRANO PREUZIMANJE (X za natrag) ---", 'loop_prompt': "Link: "},
    'cs': {'title': "Čeština", 'opt1': "Stáhnout MP3", 'opt2': "Stáhnout MP4", 'opt3': "MKV na MP4", 'opt4': "Extrahovat MP3", 'opt5': "AKTUALIZOVAT", 'opt6': "yt-dlp", 'opt7': "JAZYK", 'opt8': "Ukončit", 'loop_head': "--- KONTINUÁLNÍ STAHOVÁNÍ (X pro zpět) ---", 'loop_prompt': "Odkaz: "},
    'tr': {'title': "Türkçe", 'opt1': "MP3 İndir", 'opt2': "MP4 İndir", 'opt3': "MKV -> MP4", 'opt4': "MP3 Ayıkla", 'opt5': "GÜNCELLE", 'opt6': "yt-dlp", 'opt7': "DİL", 'opt8': "Çıkış", 'loop_head': "--- KESİNTİSİZ İNDİRME (Geri için X) ---", 'loop_prompt': "Link: "},
    'hi': {'title': "हिन्दी", 'opt1': "MP3 डाउनलोड", 'opt2': "MP4 डाउनलोड", 'opt3': "MKV -> MP4", 'opt4': "MP3 निकालें", 'opt5': "अपडेट", 'opt6': "yt-dlp", 'opt7': "भाषा", 'opt8': "बाहर", 'loop_head': "--- लगातार डाउनलोड (X वापस) ---", 'loop_prompt': "लिंक: "}
}

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

def installa_ffmpeg_auto():
    if os.path.exists(FFMPEG_EXE): return
    zip_tmp = os.path.join(os.environ.get('TEMP', 'C:\\'), "ffmpeg.zip")
    try:
        req = urllib.request.Request(FF_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_tmp, 'wb') as out: shutil.copyfileobj(response, out)
        temp_ex = r"C:\FFmpeg_Temp"
        with zipfile.ZipFile(zip_tmp, 'r') as zip_ref: zip_ref.extractall(temp_ex)
        folder = [d for d in os.listdir(temp_ex) if os.path.isdir(os.path.join(temp_ex, d))][0]
        if os.path.exists(FFMPEG_ROOT): shutil.rmtree(FFMPEG_ROOT)
        shutil.move(os.path.join(temp_ex, folder), FFMPEG_ROOT)
        shutil.rmtree(temp_ex); os.remove(zip_tmp)
    except: sys.exit()

def main():
    curr = None
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: curr = f.read().strip()
    if curr not in LANGS:
        os.system('cls' if os.name == 'nt' else 'clear')
        codes = list(LANGS.keys())
        for i, c in enumerate(codes, 1): print(f" [{i}] {LANGS[c]['title']}")
        curr = codes[int(input("Choice: "))-1]
        with open(CONFIG_FILE, 'w') as f: f.write(curr)

    L = LANGS[curr]
    for d in [BASE_DIR, MUSIC_DIR, VIDEO_DIR]: 
        if not os.path.exists(d): os.makedirs(d)
    installa_ffmpeg_auto()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===========================================")
        print(f"      SUPER DOWNLOADER PRO V2.6")
        print("===========================================")
        for i in range(1, 9): print(f" [{i}] -> {L[f'opt{i}']}")
        print("===========================================")
        
        s = input("> ").strip()
        if s == '8': break
        elif s == '7':
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            main(); break
        elif s in ['1', '2']:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(L['loop_head'])
                u = input(L['loop_prompt']).strip()
                if u.lower() == 'x': break
                if u:
                    opts = {'ffmpeg_location': os.path.join(FFMPEG_ROOT, "bin"), 'outtmpl': os.path.join(MUSIC_DIR if s=='1' else VIDEO_DIR, '%(title)s.%(ext)s'), 'noplaylist': True}
                    if s == '1': opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
                    else: opts.update({'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'})
                    with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([u])
        elif s == '3':
            for f in [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith('.mkv')]:
                subprocess.run([FFMPEG_EXE, "-i", os.path.join(VIDEO_DIR, f), "-c", "copy", os.path.join(VIDEO_DIR, os.path.splitext(f)[0] + ".mp4"), "-y"], capture_output=True)
        elif s == '4':
            for f in [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv'))]:
                subprocess.run([FFMPEG_EXE, "-i", os.path.join(VIDEO_DIR, f), "-vn", "-b:a", "192k", os.path.join(MUSIC_DIR, os.path.splitext(f)[0] + ".mp3"), "-y"], capture_output=True)
        elif s == '5':
            urllib.request.urlretrieve(UPDATE_URL, SCRIPT_PATH + ".new")
            with open("update.bat", "w") as f: f.write(f'@echo off\nmove /y "{SCRIPT_PATH}.new" "{SCRIPT_PATH}"\nstart python "{SCRIPT_PATH}"\ndel "%~f0"')
            subprocess.Popen("update.bat", shell=True); sys.exit()
        elif s == '6':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])

if __name__ == "__main__":
    main()
