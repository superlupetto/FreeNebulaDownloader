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
    'it': {'title': "Italiano", 'opt1': "Scarica MP3", 'opt2': "Scarica MP4", 'opt3': "Converti MKV in MP4", 'opt4': "Estrai MP3 da Video Locali", 'opt5': "AGGIORNA SCRIPT", 'opt6': "Aggiorna yt-dlp", 'opt7': "LINGUA", 'opt8': "Esci"},
    'en': {'title': "English", 'opt1': "Download MP3", 'opt2': "Download MP4", 'opt3': "Convert MKV to MP4", 'opt4': "Extract MP3 from Local Video", 'opt5': "UPDATE SCRIPT", 'opt6': "Update yt-dlp", 'opt7': "LANGUAGE", 'opt8': "Exit"},
    'ja': {'title': "日本語", 'opt1': "MP3ダウンロード", 'opt2': "MP4ダウンロード", 'opt3': "MKVをMP4に変換", 'opt4': "ローカルビデオからMP3を抽出", 'opt5': "スクリプト更新", 'opt6': "yt-dlp更新", 'opt7': "言語", 'opt8': "終了"},
    'da': {'title': "Dansk", 'opt1': "Download MP3", 'opt2': "Download MP4", 'opt3': "Konverter MKV til MP4", 'opt4': "Ekstraher MP3 fra lokal video", 'opt5': "OPDATER SCRIPT", 'opt6': "Opdater yt-dlp", 'opt7': "SPROG", 'opt8': "Afslut"},
    'fr': {'title': "Français", 'opt1': "Télécharger MP3", 'opt2': "Télécharger MP4", 'opt3': "Convertir MKV en MP4", 'opt4': "Extraire MP3 d'une vidéo locale", 'opt5': "MAJ SCRIPT", 'opt6': "MAJ yt-dlp", 'opt7': "LANGUE", 'opt8': "Quitter"},
    'hr': {'title': "Hrvatski", 'opt1': "Preuzmi MP3", 'opt2': "Preuzmi MP4", 'opt3': "Pretvori MKV u MP4", 'opt4': "Ekstrahiraj MP3 iz lokalnog videa", 'opt5': "AŽURIRAJ SKRIPTU", 'opt6': "Ažuriraj yt-dlp", 'opt7': "JEZIK", 'opt8': "Izlaz"},
    'cs': {'title': "Čeština", 'opt1': "Stáhnout MP3", 'opt2': "Stáhnout MP4", 'opt3': "Převést MKV na MP4", 'opt4': "Extrahovat MP3 z místního videa", 'opt5': "AKTUALIZOVAT SKRIPT", 'opt6': "Aktualizovat yt-dlp", 'opt7': "JAZYK", 'opt8': "Ukončit"},
    'tr': {'title': "Türkçe", 'opt1': "MP3 İndir", 'opt2': "MP4 İndir", 'opt3': "MKV'yi MP4'e Dönüştür", 'opt4': "Yerel Videodan MP3 Ayıkla", 'opt5': "BETİĞİ GÜNCELLE", 'opt6': "yt-dlp Güncelle", 'opt7': "DİL", 'opt8': "Çıkış"},
    'hi': {'title': "हिन्दी", 'opt1': "MP3 डाउनलोड", 'opt2': "MP4 डाउनलोड", 'opt3': "MKV को MP4 में बदलें", 'opt4': "स्थानीय वीडियो से MP3 निकालें", 'opt5': "स्क्रिप्ट अपडेट", 'opt6': "yt-dlp अपडेट", 'opt7': "भाषा", 'opt8': "बाहर निकलें"}
}

def installa_ffmpeg_auto():
    if os.path.exists(FFMPEG_EXE): return
    print("\n>>> FFMPEG INSTALLATION IN PROGRESS...")
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
    except Exception as e: print(f"Error FFmpeg: {e}"); input(); sys.exit()

def main():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f: current_code = f.read().strip()
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        codes = list(LANGS.keys())
        for i, c in enumerate(codes, 1): print(f" [{i}] {LANGS[c]['title']}")
        current_code = codes[int(input("\nChoice: "))-1]
        with open(CONFIG_FILE, 'w') as f: f.write(current_code)

    L = LANGS[current_code]
    for d in [BASE_DIR, MUSIC_DIR, VIDEO_DIR]: 
        if not os.path.exists(d): os.makedirs(d)
    installa_ffmpeg_auto()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===========================================")
        print(f"      Free SupeDownloader V2.2")
        print("===========================================")
        print(f" Path: {BASE_DIR} | Lang: {L['title']}")
        print("-------------------------------------------")
        for i in range(1, 9): print(f" [{i}] -> {L[f'opt{i}']}")
        print("===========================================")
        
        scelta = input("Choice: ").strip()
        if scelta == '8': break
        elif scelta == '7':
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            main(); break
        elif scelta in ['1', '2']:
            u = input("Link (x back): ").strip()
            if u.lower() != 'x':
                import yt_dlp
                opts = {'ffmpeg_location': os.path.join(FFMPEG_ROOT, "bin"), 'outtmpl': os.path.join(MUSIC_DIR if scelta=='1' else VIDEO_DIR, '%(title)s.%(ext)s'), 'noplaylist': True}
                if scelta == '1': opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
                else: opts.update({'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'})
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([u])
                    print("\n✅ DONE")
                except Exception as e: print(f"Error: {e}")
            input("\nENTER...")
        elif scelta == '3': # MKV -> MP4
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith('.mkv')]
            for f in files:
                print(f"🔄 Converting: {f}")
                subprocess.run([FFMPEG_EXE, "-i", os.path.join(VIDEO_DIR, f), "-c", "copy", os.path.join(VIDEO_DIR, os.path.splitext(f)[0] + ".mp4"), "-y"], capture_output=True)
            print("✅ DONE"); input("\nENTER...")
        elif scelta == '4': # Video -> MP3
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv', '.webm'))]
            for f in files:
                print(f"🎵 Extracting MP3: {f}")
                subprocess.run([FFMPEG_EXE, "-i", os.path.join(VIDEO_DIR, f), "-vn", "-b:a", "192k", os.path.join(MUSIC_DIR, os.path.splitext(f)[0] + ".mp3"), "-y"], capture_output=True)
            print("✅ DONE"); input("\nENTER...")
        elif scelta == '5':
            print("Checking updates...")
            try:
                urllib.request.urlretrieve(UPDATE_URL, SCRIPT_PATH + ".new")
                with open("update.bat", "w") as f: f.write(f'@echo off\ntimeout /t 1 >nul\nmove /y "{SCRIPT_PATH}.new" "{SCRIPT_PATH}"\nstart python "{SCRIPT_PATH}"\ndel "%~f0"')
                subprocess.Popen("update.bat", shell=True); sys.exit()
            except: print("Error: Server Offline"); input()
        elif scelta == '6':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            input("\nUPDATED. ENTER...")

if __name__ == "__main__":
    main()



