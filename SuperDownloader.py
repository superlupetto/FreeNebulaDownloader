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

# --- DIZIONARIO LINGUE ESTESO ---
LANGS = {
    'it': {'title': "Italiano", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> Scarica MP3", 'opt2': "[2] -> Scarica MP4", 'opt3': "[3] -> Converti Locali", 'opt4': "[4] -> AGGIORNA SCRIPT", 'opt5': "[5] -> Aggiorna yt-dlp", 'opt6': "[6] -> LINGUA", 'opt7': "[7] -> Esci", 'ask': "Scegli: ", 'link': "Link (x torna): ", 'done': "✅ Completato!", 'ffmpeg': "FFMPEG MANCANTE - INSTALLAZIONE..."},
    'en': {'title': "English", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> Download MP3", 'opt2': "[2] -> Download MP4", 'opt3': "[3] -> Local Convert", 'opt4': "[4] -> UPDATE SCRIPT", 'opt5': "[5] -> Update yt-dlp", 'opt6': "[6] -> LANGUAGE", 'opt7': "[7] -> Exit", 'ask': "Choose: ", 'link': "Link (x back): ", 'done': "✅ Done!", 'ffmpeg': "FFMPEG MISSING - INSTALLING..."},
    'ja': {'title': "日本語", 'menu': "スーパーダウンローダー PRO V1.9.2", 'opt1': "[1] -> MP3ダウンロード", 'opt2': "[2] -> MP4ダウンロード", 'opt3': "[3] -> ローカル変換", 'opt4': "[4] -> スクリプト更新", 'opt5': "[5] -> yt-dlp更新", 'opt6': "[6] -> 言語設定", 'opt7': "[7] -> 終了", 'ask': "選択: ", 'link': "リンク (xで戻る): ", 'done': "✅ 完了！", 'ffmpeg': "FFMPEGが見つかりません - インストール中..."},
    'da': {'title': "Dansk", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> Download MP3", 'opt2': "[2] -> Download MP4", 'opt3': "[3] -> Lokal Konvertering", 'opt4': "[4] -> OPDATER SCRIPT", 'opt5': "[5] -> Opdater yt-dlp", 'opt6': "[6] -> SPROG", 'opt7': "[7] -> Afslut", 'ask': "Vælg: ", 'link': "Link (x tilbage): ", 'done': "✅ Færdig!", 'ffmpeg': "FFMPEG MANGLER - INSTALLERER..."},
    'fr': {'title': "Français", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> Télécharger MP3", 'opt2': "[2] -> Télécharger MP4", 'opt3': "[3] -> Conversion Locale", 'opt4': "[4] -> MAJ SCRIPT", 'opt5': "[5] -> MAJ yt-dlp", 'opt6': "[6] -> LANGUE", 'opt7': "[7] -> Quitter", 'ask': "Choisir: ", 'link': "Lien (x retour): ", 'done': "✅ Terminé!", 'ffmpeg': "FFMPEG MANQUANT - INSTALLATION..."},
    'hr': {'title': "Hrvatski", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> Preuzmi MP3", 'opt2': "[2] -> Preuzmi MP4", 'opt3': "[3] -> Lokalna Konverzija", 'opt4': "[4] -> AŽURIRAJ SKRIPTU", 'opt5': "[5] -> Ažuriraj yt-dlp", 'opt6': "[6] -> JEZIK", 'opt7': "[7] -> Izlaz", 'ask': "Odaberi: ", 'link': "Link (x natrag): ", 'done': "✅ Gotovo!", 'ffmpeg': "FFMPEG NEDOSTAJE - INSTALACIJA..."},
    'cs': {'title': "Čeština", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> Stáhnout MP3", 'opt2': "[2] -> Stáhnout MP4", 'opt3': "[3] -> Lokální Konverze", 'opt4': "[4] -> AKTUALIZOVAT SKRIPT", 'opt5': "[5] -> Aktualizovat yt-dlp", 'opt6': "[6] -> JAZYK", 'opt7': "[7] -> Ukončit", 'ask': "Vyberte: ", 'link': "Odkaz (x zpět): ", 'done': "✅ Hotovo!", 'ffmpeg': "FFMPEG CHYBÍ - INSTALACE..."},
    'tr': {'title': "Türkçe", 'menu': "SUPER DOWNLOADER PRO V1.9.2", 'opt1': "[1] -> MP3 İndir", 'opt2': "[2] -> MP4 İndir", 'opt3': "[3] -> Yerel Dönüştürme", 'opt4': "[4] -> BETİĞİ GÜNCELLE", 'opt5': "[5] -> yt-dlp Güncelle", 'opt6': "[6] -> DİL", 'opt7': "[7] -> Çıkış", 'ask': "Seçiniz: ", 'link': "Link (x geri): ", 'done': "✅ Tamamlandı!", 'ffmpeg': "FFMPEG EKSİK - YÜKLENİYOR..."},
    'hi': {'title': "हिन्दी", 'menu': "सुपर डाउनलोडर PRO V1.9.2", 'opt1': "[1] -> MP3 डाउनलोड", 'opt2': "[2] -> MP4 डाउनलोड", 'opt3': "[3] -> स्थानीय रूपांतरण", 'opt4': "[4] -> स्क्रिप्ट अपडेट", 'opt5': "[5] -> yt-dlp अपडेट", 'opt6': "[6] -> भाषा", 'opt7': "[7] -> बाहर निकलें", 'ask': "चुनें: ", 'link': "लिंक (x पीछे): ", 'done': "✅ संपन्न!", 'ffmpeg': "FFMPEG गायब है - इंस्टॉल हो रहा है..."}
}

def carica_lingua():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            saved = f.read().strip()
            if saved in LANGS: return saved
    return None

def salva_lingua(lang_code):
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    with open(CONFIG_FILE, 'w') as f: f.write(lang_code)

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

def installa_ffmpeg_auto(L):
    if os.path.exists(FFMPEG_EXE): return
    print(f"\n{L['ffmpeg']}")
    zip_tmp = os.path.join(os.environ.get('TEMP', 'C:\\'), "ffmpeg_btbn.zip")
    try:
        req = urllib.request.Request(FF_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_tmp, 'wb') as out: shutil.copyfileobj(response, out)
        temp_ex = r"C:\FFmpeg_Temp"
        with zipfile.ZipFile(zip_tmp, 'r') as zip_ref: zip_ref.extractall(temp_ex)
        folder = [d for d in os.listdir(temp_ex) if os.path.isdir(os.path.join(temp_ex, d))][0]
        if os.path.exists(FFMPEG_ROOT): shutil.rmtree(FFMPEG_ROOT)
        shutil.move(os.path.join(temp_ex, folder), FFMPEG_ROOT)
        shutil.rmtree(temp_ex); os.remove(zip_tmp)
    except Exception as e: print(f"Error: {e}"); input(); sys.exit()

def download(url, mode, L):
    opts = {
        'ffmpeg_location': os.path.join(FFMPEG_ROOT, "bin"),
        'outtmpl': os.path.join(MUSIC_DIR if mode=='audio' else VIDEO_DIR, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best' if mode=='audio' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
    }
    if mode == 'audio': opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        print(f"\n{L['done']}")
    except Exception as e: print(f"Error: {e}")

def main():
    current_code = carica_lingua()
    if not current_code:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===========================================")
        print("         SELECT YOUR LANGUAGE")
        print("===========================================")
        codes = list(LANGS.keys())
        for i, code in enumerate(codes, 1): print(f" [{i}] {LANGS[code]['title']}")
        idx = int(input("\nChoice: ")) - 1
        current_code = codes[idx]
        salva_lingua(current_code)

    L = LANGS[current_code]
    for d in [BASE_DIR, MUSIC_DIR, VIDEO_DIR]: 
        if not os.path.exists(d): os.makedirs(d)
    installa_ffmpeg_auto(L)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===========================================")
        print(L['menu'])
        print("===========================================")
        print(f" Path: {BASE_DIR} | Lang: {L['title']}")
        print("-------------------------------------------")
        for i in range(1, 8): print(f" {L[f'opt{i}']}")
        print("===========================================")
        
        scelta = input(L['ask']).strip()
        if scelta == '7': break
        elif scelta == '6':
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            main(); break
        elif scelta in ['1', '2']:
            u = input(L['link']).strip()
            if u.lower() != 'x' and u: download(u, 'audio' if scelta == '1' else 'video', L)
            input("\nENTER...")
        elif scelta == '3':
            files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.mkv', '.webm'))]
            for f in files:
                out = os.path.splitext(f)[0] + ".mp3"
                subprocess.run([FFMPEG_EXE, "-i", os.path.join(VIDEO_DIR, f), "-vn", "-b:a", "192k", os.path.join(MUSIC_DIR, out), "-y"], capture_output=True)
            print(L['done']); input("\nENTER...")
        elif scelta == '4':
            urllib.request.urlretrieve(UPDATE_URL, SCRIPT_PATH + ".new")
            with open("update.bat", "w") as f: f.write(f'@echo off\ntimeout /t 1 >nul\nmove /y "{SCRIPT_PATH}.new" "{SCRIPT_PATH}"\nstart python "{SCRIPT_PATH}"\ndel "%~f0"')
            subprocess.Popen("update.bat", shell=True); sys.exit()
        elif scelta == '5':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            input("\nENTER...")

if __name__ == "__main__":
    main()
