import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import logging
import traceback
from logging.handlers import RotatingFileHandler

# --- CONFIGURAZIONE ---
USER_HOME = os.path.expanduser("~/Documenti")
BASE_DIR = os.path.join(USER_HOME, "FreeSuperDownloader")
CONFIG_FILE = os.path.join(BASE_DIR, "config.txt")
MUSIC_DIR = os.path.join(BASE_DIR, "Musica")
VIDEO_DIR = os.path.join(BASE_DIR, "Video")
FFMPEG_ROOT = os.path.join(BASE_DIR, "FFmpeg")
FFMPEG_EXE = os.path.join(FFMPEG_ROOT, "bin", "ffmpeg.exe")


UPDATE_URL = "https://raw.githubusercontent.com/superlupetto/FreeSuperDownloader/main/freeSuperDownloader.py"
FF_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
SCRIPT_PATH = os.path.abspath(__file__)
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

LANGS = {
    'it': {
        'title': "Italiano",
        'opt1': "Scarica Modalità mp4-mp3",
        'opt2': "Converti MKV in MP4",
        'opt3': "Estrai Video da mp3 Locali",
        'opt4': "AGGIORNA SCRIPT",
        'opt5': "Aggiorna yt-dlp",
        'opt6': "LINGUA",
        'opt7': "Esci",
        'loop_head': "--- MODALITÀ DOWNLOAD (X per uscire | Scrivi 'mp3' o 'mp4' per cambiare) ---",
        'loop_mode': "Modalità attuale: {mode}",
        'loop_prompt': "Link: ",
        'msg_press_enter': "\nPremi INVIO per continuare...",
        'msg_error': "[ERRORE]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg non trovato. Download automatico in corso...",
        'msg_ffmpeg_ok': "FFmpeg installato correttamente.",
        'msg_ffmpeg_fail': "Installazione automatica di FFmpeg fallita.",
        'msg_download_ok': "Download completato.",
        'msg_download_fail': "Download fallito.",
        'msg_mode_change': "Modalità cambiata in: {mode}",
        'msg_conv_done': "Conversione completata. File convertiti: {ok}. Errori: {err}.",
        'msg_extract_done': "Estrazione completata. File creati: {ok}. Errori: {err}.",
        'msg_update_script_dl': "Download aggiornamento script...",
        'msg_update_script_ok': "Aggiornamento scaricato. Riavvio dello script...",
        'msg_update_script_fail': "Aggiornamento script fallito.",
        'msg_update_ytdlp': "Aggiornamento yt-dlp in corso...",
        'msg_update_ytdlp_ok': "yt-dlp aggiornato correttamente.",
        'msg_update_ytdlp_fail': "Aggiornamento yt-dlp fallito.",
        'msg_log_saved': "Log salvato in: ",
        'msg_conv_error_file': "Errore conversione",
        'msg_no_files': "Nessun file trovato da elaborare.",
        'msg_invalid_choice': "Scelta non valida.",
    },
    'en': {
        'title': "English",
        'opt1': "Download (Loop Mode)", 'opt2': "Convert MKV to MP4",
        'opt3': "Extract MP3", 'opt4': "UPDATE SCRIPT", 'opt5': "Update yt-dlp",
        'opt6': "LANGUAGE", 'opt7': "Exit",
        'loop_head': "--- DOWNLOAD MODE (X to exit | Type 'mp3' or 'mp4' to switch) ---",
        'loop_mode': "Current mode: {mode}",
        'loop_prompt': "Link: ", 'msg_press_enter': "\nPress ENTER to continue...",
        'msg_error': "[ERROR]", 'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg not found. Automatic download in progress...",
        'msg_ffmpeg_ok': "FFmpeg installed successfully.",
        'msg_ffmpeg_fail': "Automatic FFmpeg installation failed.",
        'msg_download_ok': "Download completed.", 'msg_download_fail': "Download failed.",
        'msg_mode_change': "Mode changed to: {mode}",
        'msg_conv_done': "Conversion completed. Converted files: {ok}. Errors: {err}.",
        'msg_extract_done': "Extraction completed. Created files: {ok}. Errors: {err}.",
        'msg_update_script_dl': "Downloading script update...",
        'msg_update_script_ok': "Update downloaded. Restarting script...",
        'msg_update_script_fail': "Script update failed.",
        'msg_update_ytdlp': "Updating yt-dlp...", 'msg_update_ytdlp_ok': "yt-dlp updated successfully.",
        'msg_update_ytdlp_fail': "yt-dlp update failed.",
        'msg_log_saved': "Log saved at: ", 'msg_conv_error_file': "Conversion error",
        'msg_no_files': "No files found to process.", 'msg_invalid_choice': "Invalid choice.",
    },
    'fr': {'title': "Français", 'opt1': "Télécharger (Loop)", 'opt2': "MKV->MP4", 'opt3': "Extr MP3", 'opt4': "MAJ", 'opt5': "yt-dlp", 'opt6': "LANG", 'opt7': "Sortie", 'loop_head': "--- MODE TELECHARGEMENT (X pour sortir | 'mp3'/'mp4' pour changer) ---", 'loop_mode': "Mode actuel: {mode}", 'loop_prompt': "Lien: ", 'msg_press_enter': "\nENTREE pour continuer...", 'msg_error': "[ERREUR]", 'msg_info': "[INFO]", 'msg_ffmpeg_missing': "FFmpeg manquant...", 'msg_ffmpeg_ok': "FFmpeg OK.", 'msg_ffmpeg_fail': "Fail FFmpeg.", 'msg_download_ok': "OK.", 'msg_download_fail': "Fail.", 'msg_mode_change': "Mode changé: {mode}", 'msg_conv_done': "Converti: {ok}. Err: {err}.", 'msg_extract_done': "Extrait: {ok}. Err: {err}.", 'msg_update_script_dl': "MAJ...", 'msg_update_script_ok': "MAJ OK.", 'msg_update_script_fail': "MAJ Fail.", 'msg_update_ytdlp': "MAJ yt-dlp...", 'msg_update_ytdlp_ok': "OK.", 'msg_update_ytdlp_fail': "Fail.", 'msg_log_saved': "Log: ", 'msg_conv_error_file': "Err conv", 'msg_no_files': "Pas de fichiers.", 'msg_invalid_choice': "Invalide."},
}

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausa(L):
    pass

def mostra_info(L, msg):
    print(f"\n{L['msg_info']} {msg}")

def mostra_errore(L, titolo, err=None):
    print(f"\n{L['msg_error']} {titolo}")
    if err is not None:
        print(f"Dettagli: {err}")
    print(f"{L['msg_log_saved']}{LOG_FILE}")

def init_logger():
    os.makedirs(BASE_DIR, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    if logger.handlers: return
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_errore(contesto, err):
    logging.error("%s | %s", contesto, err)
    logging.error(traceback.format_exc())

def installa_ffmpeg_auto(L):
    if os.path.exists(FFMPEG_EXE):
        return True

    zip_tmp = os.path.join(BASE_DIR, "ffmpeg_temp.zip")
    temp_ex = os.path.join(BASE_DIR, "ffmpeg_extract")

    try:
        mostra_info(L, L['msg_ffmpeg_missing'])
        req = urllib.request.Request(FF_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(zip_tmp, 'wb') as out:
            shutil.copyfileobj(response, out)

        if os.path.exists(temp_ex):
            shutil.rmtree(temp_ex, ignore_errors=True)
        
        with zipfile.ZipFile(zip_tmp, 'r') as zip_ref:
            zip_ref.extractall(temp_ex)

        cartelle = [d for d in os.listdir(temp_ex) if os.path.isdir(os.path.join(temp_ex, d))]
        if not cartelle:
            raise RuntimeError("Cartella FFmpeg estratta non trovata.")
        
        folder = cartelle[0]
        
        if os.path.exists(FFMPEG_ROOT):
            shutil.rmtree(FFMPEG_ROOT, ignore_errors=True)
        
        shutil.move(os.path.join(temp_ex, folder), FFMPEG_ROOT)

        if os.path.exists(temp_ex): shutil.rmtree(temp_ex)
        if os.path.exists(zip_tmp): os.remove(zip_tmp)

        mostra_info(L, L['msg_ffmpeg_ok'])
        return True

    except Exception as e:
        log_errore("Installazione FFmpeg fallita", e)
        mostra_errore(L, L['msg_ffmpeg_fail'], e)
        pausa(L)
        return False

def normalizza_lingua(raw):
    if not raw: return None
    raw = raw.strip().lower()
    aliases = {'it': 'it', 'en': 'en', 'fr': 'fr'}
    return aliases.get(raw, raw if raw in LANGS else 'it')

def scegli_lingua():
    clear_screen()
    codes = list(LANGS.keys())
    for i, c in enumerate(codes, 1):
        print(f" [{i}] {LANGS[c]['title']}")
    try:
        choice = int(input("> ").strip())
        curr = codes[choice - 1]
    except:
        curr = 'it'
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(curr)
    return curr

def converti_mkv_a_mp4(L):
    convertiti, errori, trovati = 0, 0, False
    for f in os.listdir(VIDEO_DIR):
        if f.lower().endswith('.mkv'):
            trovati = True
            n = os.path.splitext(f)[0]
            origine = os.path.join(VIDEO_DIR, f)
            destinazione = os.path.join(VIDEO_DIR, f"{n}.mp4")
            try:
                result = subprocess.run([FFMPEG_EXE, "-i", origine, "-c", "copy", destinazione, "-y"], capture_output=True, text=True)
                if result.returncode == 0: convertiti += 1
                else: errori += 1
            except Exception as e:
                errori += 1
                log_errore(f"Conv MKV {f}", e)
    
    if not trovati: mostra_info(L, L['msg_no_files'])
    else: mostra_info(L, L['msg_conv_done'].format(ok=convertiti, err=errori))
    pausa(L)

def estrai_mp3(L):
    estratti, errori, trovati = 0, 0, False
    for f in os.listdir(VIDEO_DIR):
        if f.lower().endswith(('.mp4', '.mkv')):
            trovati = True
            n = os.path.splitext(f)[0]
            origine = os.path.join(VIDEO_DIR, f)
            destinazione = os.path.join(MUSIC_DIR, f"{n}.mp3")
            try:
                result = subprocess.run([FFMPEG_EXE, "-i", origine, "-vn", "-b:a", "192k", destinazione, "-y"], capture_output=True, text=True)
                if result.returncode == 0: estratti += 1
                else: errori += 1
            except Exception as e:
                errori += 1
                log_errore(f"Extr MP3 {f}", e)
    
    if not trovati: mostra_info(L, L['msg_no_files'])
    else: mostra_info(L, L['msg_extract_done'].format(ok=estratti, err=errori))
    pausa(L)

def aggiorna_script(L):
    try:
        mostra_info(L, L['msg_update_script_dl'])
        urllib.request.urlretrieve(UPDATE_URL, SCRIPT_PATH + ".new")
        with open("update.bat", "w", encoding='utf-8') as f:
            f.write(f'@echo off\ntimeout /t 1 >nul\nmove /y "{SCRIPT_PATH}.new" "{SCRIPT_PATH}"\nstart python "{SCRIPT_PATH}"\ndel "%~f0"')
        mostra_info(L, L['msg_update_script_ok'])
        pausa(L)
        subprocess.Popen("update.bat", shell=True)
        sys.exit()
    except Exception as e:
        log_errore("Aggiornamento script fallito", e)
        mostra_errore(L, L['msg_update_script_fail'], e)
        pausa(L)

def aggiorna_ytdlp(L):
    try:
        mostra_info(L, L['msg_update_ytdlp'])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
        mostra_info(L, L['msg_update_ytdlp_ok'])
    except Exception as e:
        log_errore("Aggiornamento yt-dlp fallito", e)
        mostra_errore(L, L['msg_update_ytdlp_fail'], e)
    pausa(L)

def download_loop(L):
    # Modalità predefinita: MP4 (H.264/AAC)
    mode = "mp3"
    
    while True:
        clear_screen()
        print(L['loop_head'])
        print(L['loop_mode'].format(mode=mode.upper()))
        
        u = input(L['loop_prompt']).strip()
        
        if u.lower() == 'x':
            break
        
        # Comandi speciali per cambiare modalità
        if u.lower() == 'mp3':
            mode = 'mp3'
            print(f"\n{L['msg_mode_change'].format(mode='MP3')}")
            pausa(L)
            continue
        elif u.lower() == 'mp4':
            mode = 'mp4'
            print(f"\n{L['msg_mode_change'].format(mode='MP4')}")
            pausa(L)
            continue
            
        if not u:
            continue

        # Configurazione base
        opts = {
            'ffmpeg_location': os.path.join(FFMPEG_ROOT, "bin"),
            'outtmpl': os.path.join(MUSIC_DIR if mode == 'mp3' else VIDEO_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'no_warnings': True,
        }

        if mode == 'mp3':
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            })
        else: # MP4
            opts.update({
                'format': 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[acodec^=mp4a][ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
                'postprocessor_args': ['-movflags', '+faststart'],
            })

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([u])
            mostra_info(L, L['msg_download_ok'])
        except Exception as e:
            log_errore(f"Download fallito: {u}", e)
            mostra_errore(L, L['msg_download_fail'], e)

        pausa(L)

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)
    init_logger()

    curr = None
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                raw = f.read().strip()
            curr = normalizza_lingua(raw)
        except: pass

    if curr not in LANGS:
        curr = scegli_lingua()
    
    L = LANGS[curr]

    if not installa_ffmpeg_auto(L):
        return

    while True:
        clear_screen()
        print("===================================================")
        print("           SUPER DOWNLOADER PRO V3.0")
        print("===================================================")
        print(os.path.expandvars(r"  %USERPROFILE%\Documents\FreeSuperDownloader"))
        print("===================================================")
        for i in range(1, 8):
            print(f" [{i}] -> {L.get(f'opt{i}', '?')}")
        print("===================================================")

        s = input("> ").strip()

        if s == '7': break
        elif s == '6':
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            curr = scegli_lingua()
            L = LANGS[curr]
        elif s == '1': download_loop(L)
        elif s == '2': converti_mkv_a_mp4(L)
        elif s == '3': estrai_mp3(L)
        elif s == '4': aggiorna_script(L)
        elif s == '5': aggiorna_ytdlp(L)
        else: mostra_info(L, L['msg_invalid_choice']); pausa(L)

if __name__ == "__main__":
    main()
