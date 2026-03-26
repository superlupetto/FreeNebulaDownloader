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
BASE_DIR = r"C:\FreeSuperDownloader"
CONFIG_FILE = os.path.join(BASE_DIR, "config.txt")
MUSIC_DIR = os.path.join(BASE_DIR, "Musica")
VIDEO_DIR = os.path.join(BASE_DIR, "Video")
FFMPEG_ROOT = r"C:\FFmpeg"
FFMPEG_EXE = os.path.join(FFMPEG_ROOT, "bin", "ffmpeg.exe")
UPDATE_URL = "https://raw.githubusercontent.com/superlupetto/FreeSuperDownloader/main/freeSuperDownloader.py"
FF_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
SCRIPT_PATH = os.path.abspath(__file__)
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

LANGS = {
    'it': {
        'title': "Italiano",
        'opt1': "Scarica MP3",
        'opt2': "Scarica MP4",
        'opt3': "Converti MKV in MP4",
        'opt4': "Estrai MP3 da Video Locali",
        'opt5': "AGGIORNA SCRIPT",
        'opt6': "Aggiorna yt-dlp",
        'opt7': "LINGUA",
        'opt8': "Esci",
        'loop_head': "--- DOWNLOAD CONTINUO (X per uscire) ---",
        'loop_prompt': "Link: ",
        'msg_press_enter': "\nPremi INVIO per continuare...",
        'msg_error': "[ERRORE]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg non trovato. Download automatico in corso...",
        'msg_ffmpeg_ok': "FFmpeg installato correttamente.",
        'msg_ffmpeg_fail': "Installazione automatica di FFmpeg fallita.",
        'msg_download_ok': "Download completato.",
        'msg_download_fail': "Download fallito.",
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
        'msg_extract_error_file': "Errore estrazione MP3",
        'msg_no_files': "Nessun file trovato da elaborare.",
        'msg_invalid_choice': "Scelta non valida.",
        'msg_op_fail_for': "Operazione fallita per {file}"
    },
    'en': {
        'title': "English",
        'opt1': "Download MP3",
        'opt2': "Download MP4",
        'opt3': "Convert MKV to MP4",
        'opt4': "Extract MP3",
        'opt5': "UPDATE SCRIPT",
        'opt6': "Update yt-dlp",
        'opt7': "LANGUAGE",
        'opt8': "Exit",
        'loop_head': "--- CONTINUOUS DOWNLOAD (X to exit) ---",
        'loop_prompt': "Link: ",
        'msg_press_enter': "\nPress ENTER to continue...",
        'msg_error': "[ERROR]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg not found. Automatic download in progress...",
        'msg_ffmpeg_ok': "FFmpeg installed successfully.",
        'msg_ffmpeg_fail': "Automatic FFmpeg installation failed.",
        'msg_download_ok': "Download completed.",
        'msg_download_fail': "Download failed.",
        'msg_conv_done': "Conversion completed. Converted files: {ok}. Errors: {err}.",
        'msg_extract_done': "Extraction completed. Created files: {ok}. Errors: {err}.",
        'msg_update_script_dl': "Downloading script update...",
        'msg_update_script_ok': "Update downloaded. Restarting script...",
        'msg_update_script_fail': "Script update failed.",
        'msg_update_ytdlp': "Updating yt-dlp...",
        'msg_update_ytdlp_ok': "yt-dlp updated successfully.",
        'msg_update_ytdlp_fail': "yt-dlp update failed.",
        'msg_log_saved': "Log saved at: ",
        'msg_conv_error_file': "Conversion error",
        'msg_extract_error_file': "MP3 extraction error",
        'msg_no_files': "No files found to process.",
        'msg_invalid_choice': "Invalid choice.",
        'msg_op_fail_for': "Operation failed for {file}"
    },
    'ja': {
        'title': "日本語",
        'opt1': "MP3ダウンロード",
        'opt2': "MP4ダウンロード",
        'opt3': "MKV変換",
        'opt4': "MP3抽出",
        'opt5': "更新",
        'opt6': "yt-dlp更新",
        'opt7': "言語",
        'opt8': "終了",
        'loop_head': "--- 連続ダウンロード (Xで戻る) ---",
        'loop_prompt': "リンク: ",
        'msg_press_enter': "\n続行するにはEnterを押してください...",
        'msg_error': "[エラー]",
        'msg_info': "[情報]",
        'msg_ffmpeg_missing': "FFmpeg が見つかりません。自動ダウンロード中...",
        'msg_ffmpeg_ok': "FFmpeg のインストールが完了しました。",
        'msg_ffmpeg_fail': "FFmpeg の自動インストールに失敗しました。",
        'msg_download_ok': "ダウンロード完了。",
        'msg_download_fail': "ダウンロード失敗。",
        'msg_conv_done': "変換完了。成功: {ok} 件。失敗: {err} 件。",
        'msg_extract_done': "抽出完了。成功: {ok} 件。失敗: {err} 件。",
        'msg_update_script_dl': "スクリプト更新をダウンロード中...",
        'msg_update_script_ok': "更新を取得しました。スクリプトを再起動します...",
        'msg_update_script_fail': "スクリプト更新に失敗しました。",
        'msg_update_ytdlp': "yt-dlp を更新中...",
        'msg_update_ytdlp_ok': "yt-dlp を更新しました。",
        'msg_update_ytdlp_fail': "yt-dlp の更新に失敗しました。",
        'msg_log_saved': "ログ保存先: ",
        'msg_conv_error_file': "変換エラー",
        'msg_extract_error_file': "MP3抽出エラー",
        'msg_no_files': "処理するファイルが見つかりません。",
        'msg_invalid_choice': "無効な選択です。",
        'msg_op_fail_for': "{file} の処理に失敗しました"
    },
    'da': {
        'title': "Dansk",
        'opt1': "Download MP3",
        'opt2': "Download MP4",
        'opt3': "MKV til MP4",
        'opt4': "Ekstraher MP3",
        'opt5': "OPDATER",
        'opt6': "yt-dlp",
        'opt7': "SPROG",
        'opt8': "Afslut",
        'loop_head': "--- LØBENDE DOWNLOAD (X for menu) ---",
        'loop_prompt': "Link: ",
        'msg_press_enter': "\nTryk ENTER for at fortsætte...",
        'msg_error': "[FEJL]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg blev ikke fundet. Automatisk download er i gang...",
        'msg_ffmpeg_ok': "FFmpeg blev installeret korrekt.",
        'msg_ffmpeg_fail': "Automatisk installation af FFmpeg mislykkedes.",
        'msg_download_ok': "Download fuldført.",
        'msg_download_fail': "Download mislykkedes.",
        'msg_conv_done': "Konvertering færdig. Konverterede filer: {ok}. Fejl: {err}.",
        'msg_extract_done': "Udtrækning færdig. Oprettede filer: {ok}. Fejl: {err}.",
        'msg_update_script_dl': "Downloader script-opdatering...",
        'msg_update_script_ok': "Opdatering hentet. Genstarter scriptet...",
        'msg_update_script_fail': "Script-opdatering mislykkedes.",
        'msg_update_ytdlp': "Opdaterer yt-dlp...",
        'msg_update_ytdlp_ok': "yt-dlp blev opdateret korrekt.",
        'msg_update_ytdlp_fail': "Opdatering af yt-dlp mislykkedes.",
        'msg_log_saved': "Log gemt i: ",
        'msg_conv_error_file': "Konverteringsfejl",
        'msg_extract_error_file': "MP3-udtræksfejl",
        'msg_no_files': "Ingen filer fundet til behandling.",
        'msg_invalid_choice': "Ugyldigt valg.",
        'msg_op_fail_for': "Operation mislykkedes for {file}"
    },
    'fr': {
        'title': "Français",
        'opt1': "Télécharger MP3",
        'opt2': "Télécharger MP4",
        'opt3': "MKV vers MP4",
        'opt4': "Extraire MP3",
        'opt5': "MAJ",
        'opt6': "yt-dlp",
        'opt7': "LANGUE",
        'opt8': "Quitter",
        'loop_head': "--- TÉLÉCHARGEMENT CONTINU (X pour retour) ---",
        'loop_prompt': "Lien: ",
        'msg_press_enter': "\nAppuyez sur ENTRÉE pour continuer...",
        'msg_error': "[ERREUR]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg introuvable. Téléchargement automatique en cours...",
        'msg_ffmpeg_ok': "FFmpeg installé correctement.",
        'msg_ffmpeg_fail': "Échec de l'installation automatique de FFmpeg.",
        'msg_download_ok': "Téléchargement terminé.",
        'msg_download_fail': "Échec du téléchargement.",
        'msg_conv_done': "Conversion terminée. Fichiers convertis : {ok}. Erreurs : {err}.",
        'msg_extract_done': "Extraction terminée. Fichiers créés : {ok}. Erreurs : {err}.",
        'msg_update_script_dl': "Téléchargement de la mise à jour du script...",
        'msg_update_script_ok': "Mise à jour téléchargée. Redémarrage du script...",
        'msg_update_script_fail': "Échec de la mise à jour du script.",
        'msg_update_ytdlp': "Mise à jour de yt-dlp...",
        'msg_update_ytdlp_ok': "yt-dlp mis à jour correctement.",
        'msg_update_ytdlp_fail': "Échec de la mise à jour de yt-dlp.",
        'msg_log_saved': "Journal enregistré dans : ",
        'msg_conv_error_file': "Erreur de conversion",
        'msg_extract_error_file': "Erreur d'extraction MP3",
        'msg_no_files': "Aucun fichier à traiter.",
        'msg_invalid_choice': "Choix invalide.",
        'msg_op_fail_for': "Opération échouée pour {file}"
    },
    'hr': {
        'title': "Hrvatski",
        'opt1': "Preuzmi MP3",
        'opt2': "Preuzmi MP4",
        'opt3': "MKV u MP4",
        'opt4': "Ekstrakcija MP3",
        'opt5': "AŽURIRAJ",
        'opt6': "yt-dlp",
        'opt7': "JEZIK",
        'opt8': "Izlaz",
        'loop_head': "--- KONTINUIRANO PREUZIMANJE (X za natrag) ---",
        'loop_prompt': "Link: ",
        'msg_press_enter': "\nPritisni ENTER za nastavak...",
        'msg_error': "[GREŠKA]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg nije pronađen. Automatsko preuzimanje u tijeku...",
        'msg_ffmpeg_ok': "FFmpeg je uspješno instaliran.",
        'msg_ffmpeg_fail': "Automatska instalacija FFmpeg-a nije uspjela.",
        'msg_download_ok': "Preuzimanje završeno.",
        'msg_download_fail': "Preuzimanje nije uspjelo.",
        'msg_conv_done': "Pretvorba završena. Pretvoreno: {ok}. Greške: {err}.",
        'msg_extract_done': "Ekstrakcija završena. Napravljeno: {ok}. Greške: {err}.",
        'msg_update_script_dl': "Preuzimam ažuriranje skripte...",
        'msg_update_script_ok': "Ažuriranje preuzeto. Ponovno pokretanje skripte...",
        'msg_update_script_fail': "Ažuriranje skripte nije uspjelo.",
        'msg_update_ytdlp': "Ažuriram yt-dlp...",
        'msg_update_ytdlp_ok': "yt-dlp uspješno ažuriran.",
        'msg_update_ytdlp_fail': "Ažuriranje yt-dlp nije uspjelo.",
        'msg_log_saved': "Log spremljen u: ",
        'msg_conv_error_file': "Greška pretvorbe",
        'msg_extract_error_file': "Greška MP3 ekstrakcije",
        'msg_no_files': "Nema datoteka za obradu.",
        'msg_invalid_choice': "Nevažeći odabir.",
        'msg_op_fail_for': "Operacija nije uspjela za {file}"
    },
    'cs': {
        'title': "Čeština",
        'opt1': "Stáhnout MP3",
        'opt2': "Stáhnout MP4",
        'opt3': "MKV na MP4",
        'opt4': "Extrahovat MP3",
        'opt5': "AKTUALIZOVAT",
        'opt6': "yt-dlp",
        'opt7': "JAZYK",
        'opt8': "Ukončit",
        'loop_head': "--- KONTINUÁLNÍ STAHOVÁNÍ (X pro zpět) ---",
        'loop_prompt': "Odkaz: ",
        'msg_press_enter': "\nPokračujte stisknutím ENTER...",
        'msg_error': "[CHYBA]",
        'msg_info': "[INFO]",
        'msg_ffmpeg_missing': "FFmpeg nebyl nalezen. Probíhá automatické stažení...",
        'msg_ffmpeg_ok': "FFmpeg byl úspěšně nainstalován.",
        'msg_ffmpeg_fail': "Automatická instalace FFmpeg selhala.",
        'msg_download_ok': "Stahování dokončeno.",
        'msg_download_fail': "Stahování selhalo.",
        'msg_conv_done': "Konverze dokončena. Převedeno: {ok}. Chyby: {err}.",
        'msg_extract_done': "Extrakce dokončena. Vytvořeno: {ok}. Chyby: {err}.",
        'msg_update_script_dl': "Stahuji aktualizaci skriptu...",
        'msg_update_script_ok': "Aktualizace stažena. Restartuji skript...",
        'msg_update_script_fail': "Aktualizace skriptu selhala.",
        'msg_update_ytdlp': "Aktualizuji yt-dlp...",
        'msg_update_ytdlp_ok': "yt-dlp byl úspěšně aktualizován.",
        'msg_update_ytdlp_fail': "Aktualizace yt-dlp selhala.",
        'msg_log_saved': "Log uložen v: ",
        'msg_conv_error_file': "Chyba konverze",
        'msg_extract_error_file': "Chyba extrakce MP3",
        'msg_no_files': "Nebyly nalezeny žádné soubory ke zpracování.",
        'msg_invalid_choice': "Neplatná volba.",
        'msg_op_fail_for': "Operace selhala pro {file}"
    },
    'tr': {
        'title': "Türkçe",
        'opt1': "MP3 İndir",
        'opt2': "MP4 İndir",
        'opt3': "MKV -> MP4",
        'opt4': "MP3 Ayıkla",
        'opt5': "GÜNCELLE",
        'opt6': "yt-dlp",
        'opt7': "DİL",
        'opt8': "Çıkış",
        'loop_head': "--- KESİNTİSİZ İNDİRME (Geri için X) ---",
        'loop_prompt': "Link: ",
        'msg_press_enter': "\nDevam etmek için ENTER'a basın...",
        'msg_error': "[HATA]",
        'msg_info': "[BİLGİ]",
        'msg_ffmpeg_missing': "FFmpeg bulunamadı. Otomatik indirme başlatılıyor...",
        'msg_ffmpeg_ok': "FFmpeg başarıyla kuruldu.",
        'msg_ffmpeg_fail': "FFmpeg otomatik kurulumu başarısız oldu.",
        'msg_download_ok': "İndirme tamamlandı.",
        'msg_download_fail': "İndirme başarısız oldu.",
        'msg_conv_done': "Dönüştürme tamamlandı. Başarılı: {ok}. Hata: {err}.",
        'msg_extract_done': "Ayıklama tamamlandı. Oluşturulan: {ok}. Hata: {err}.",
        'msg_update_script_dl': "Betik güncellemesi indiriliyor...",
        'msg_update_script_ok': "Güncelleme indirildi. Betik yeniden başlatılıyor...",
        'msg_update_script_fail': "Betik güncellemesi başarısız oldu.",
        'msg_update_ytdlp': "yt-dlp güncelleniyor...",
        'msg_update_ytdlp_ok': "yt-dlp başarıyla güncellendi.",
        'msg_update_ytdlp_fail': "yt-dlp güncellemesi başarısız oldu.",
        'msg_log_saved': "Kayıt dosyası: ",
        'msg_conv_error_file': "Dönüştürme hatası",
        'msg_extract_error_file': "MP3 ayıklama hatası",
        'msg_no_files': "İşlenecek dosya bulunamadı.",
        'msg_invalid_choice': "Geçersiz seçim.",
        'msg_op_fail_for': "{file} için işlem başarısız oldu"
    },
    'hi': {
        'title': "हिन्दी",
        'opt1': "MP3 डाउनलोड",
        'opt2': "MP4 डाउनलोड",
        'opt3': "MKV -> MP4",
        'opt4': "MP3 निकालें",
        'opt5': "अपडेट",
        'opt6': "yt-dlp",
        'opt7': "भाषा",
        'opt8': "बाहर",
        'loop_head': "--- लगातार डाउनलोड (X वापस) ---",
        'loop_prompt': "लिंक: ",
        'msg_press_enter': "\nजारी रखने के लिए ENTER दबाएँ...",
        'msg_error': "[त्रुटि]",
        'msg_info': "[जानकारी]",
        'msg_ffmpeg_missing': "FFmpeg नहीं मिला। स्वचालित डाउनलोड चल रहा है...",
        'msg_ffmpeg_ok': "FFmpeg सफलतापूर्वक इंस्टॉल हो गया।",
        'msg_ffmpeg_fail': "FFmpeg का स्वचालित इंस्टॉल असफल रहा।",
        'msg_download_ok': "डाउनलोड पूरा हुआ।",
        'msg_download_fail': "डाउनलोड असफल रहा।",
        'msg_conv_done': "कन्वर्ज़न पूरा। सफल: {ok}. त्रुटियाँ: {err}.",
        'msg_extract_done': "एक्सट्रैक्शन पूरा। बनी फाइलें: {ok}. त्रुटियाँ: {err}.",
        'msg_update_script_dl': "स्क्रिप्ट अपडेट डाउनलोड हो रहा है...",
        'msg_update_script_ok': "अपडेट डाउनलोड हो गया। स्क्रिप्ट फिर से शुरू हो रही है...",
        'msg_update_script_fail': "स्क्रिप्ट अपडेट असफल रहा।",
        'msg_update_ytdlp': "yt-dlp अपडेट हो रहा है...",
        'msg_update_ytdlp_ok': "yt-dlp सफलतापूर्वक अपडेट हो गया।",
        'msg_update_ytdlp_fail': "yt-dlp अपडेट असफल रहा।",
        'msg_log_saved': "लॉग सहेजा गया: ",
        'msg_conv_error_file': "कन्वर्ज़न त्रुटि",
        'msg_extract_error_file': "MP3 एक्सट्रैक्शन त्रुटि",
        'msg_no_files': "प्रोसेस करने के लिए कोई फाइल नहीं मिली।",
        'msg_invalid_choice': "अमान्य चयन।",
        'msg_op_fail_for': "{file} के लिए ऑपरेशन असफल रहा"
    }
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

    if logger.handlers:
        return

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_errore(contesto, err):
    logging.error("%s | %s", contesto, err)
    logging.error(traceback.format_exc())


def installa_ffmpeg_auto(L):
    if os.path.exists(FFMPEG_EXE):
        return True

    zip_tmp = os.path.join(os.environ.get('TEMP', 'C:\\'), "ffmpeg.zip")
    temp_ex = r"C:\FFmpeg_Temp"

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

        shutil.rmtree(temp_ex, ignore_errors=True)
        if os.path.exists(zip_tmp):
            os.remove(zip_tmp)

        mostra_info(L, L['msg_ffmpeg_ok'])
        return True

    except Exception as e:
        log_errore("Installazione FFmpeg fallita", e)
        mostra_errore(L, L['msg_ffmpeg_fail'], e)
        pausa(L)
        return False


def normalizza_lingua(raw):
    if not raw:
        return None

    raw = raw.strip().lower()

    aliases = {
        'it': 'it', 'ita': 'it', 'italiano': 'it', 'lingua=it': 'it', 'lingua=ita': 'it', 'lingua=italiano': 'it',
        'en': 'en', 'eng': 'en', 'english': 'en', 'lingua=en': 'en', 'lingua=eng': 'en', 'lingua=english': 'en',
        'ja': 'ja', 'jp': 'ja', 'japanese': 'ja', 'giapponese': 'ja', 'lingua=ja': 'ja', 'lingua=jp': 'ja',
        'da': 'da', 'danish': 'da', 'dansk': 'da',
        'fr': 'fr', 'fra': 'fr', 'fre': 'fr', 'french': 'fr', 'francais': 'fr', 'français': 'fr',
        'hr': 'hr', 'croatian': 'hr', 'hrvatski': 'hr',
        'cs': 'cs', 'czech': 'cs', 'ceština': 'cs', 'čeština': 'cs',
        'tr': 'tr', 'turkish': 'tr', 'türkçe': 'tr',
        'hi': 'hi', 'hindi': 'hi', 'हिन्दी': 'hi',
    }

    if raw in aliases:
        return aliases[raw]

    if '=' in raw:
        _, value = raw.split('=', 1)
        raw = value.strip()
        return aliases.get(raw, raw)

    return raw


def scegli_lingua():
    clear_screen()
    codes = list(LANGS.keys())

    for i, c in enumerate(codes, 1):
        print(f" [{i}] {LANGS[c]['title']}")

    try:
        choice = int(input("> ").strip())
        curr = codes[choice - 1]
    except Exception:
        curr = 'it'

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(curr)

    return curr


def converti_mkv_a_mp4(L):
    convertiti = 0
    errori = 0
    trovati = False

    for f in os.listdir(VIDEO_DIR):
        if f.lower().endswith('.mkv'):
            trovati = True
            n = os.path.splitext(f)[0]
            origine = os.path.join(VIDEO_DIR, f)
            destinazione = os.path.join(VIDEO_DIR, f"{n}.mp4")

            try:
                result = subprocess.run([
                    FFMPEG_EXE,
                    "-i", origine,
                    "-c", "copy",
                    destinazione,
                    "-y"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    convertiti += 1
                else:
                    errori += 1
                    msg = (result.stderr or "")[:500]
                    logging.error("Conversione MKV->MP4 fallita per %s | %s", f, msg)
                    print(f"\n{L['msg_conv_error_file']}: {f}")
                    if msg:
                        print(msg)

            except Exception as e:
                errori += 1
                log_errore(f"Conversione MKV->MP4 fallita per {f}", e)
                mostra_errore(L, L['msg_op_fail_for'].format(file=f), e)

    if not trovati:
        mostra_info(L, L['msg_no_files'])
    else:
        mostra_info(L, L['msg_conv_done'].format(ok=convertiti, err=errori))

    pausa(L)


def estrai_mp3(L):
    estratti = 0
    errori = 0
    trovati = False

    for f in os.listdir(VIDEO_DIR):
        if f.lower().endswith(('.mp4', '.mkv')):
            trovati = True
            n = os.path.splitext(f)[0]
            origine = os.path.join(VIDEO_DIR, f)
            destinazione = os.path.join(MUSIC_DIR, f"{n}.mp3")

            try:
                result = subprocess.run([
                    FFMPEG_EXE,
                    "-i", origine,
                    "-vn",
                    "-b:a", "192k",
                    destinazione,
                    "-y"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    estratti += 1
                else:
                    errori += 1
                    msg = (result.stderr or "")[:500]
                    logging.error("Estrazione MP3 fallita per %s | %s", f, msg)
                    print(f"\n{L['msg_extract_error_file']}: {f}")
                    if msg:
                        print(msg)

            except Exception as e:
                errori += 1
                log_errore(f"Estrazione MP3 fallita per {f}", e)
                mostra_errore(L, L['msg_op_fail_for'].format(file=f), e)

    if not trovati:
        mostra_info(L, L['msg_no_files'])
    else:
        mostra_info(L, L['msg_extract_done'].format(ok=estratti, err=errori))

    pausa(L)


def aggiorna_script(L):
    try:
        mostra_info(L, L['msg_update_script_dl'])
        urllib.request.urlretrieve(UPDATE_URL, SCRIPT_PATH + ".new")

        with open("update.bat", "w", encoding='utf-8') as f:
            f.write(
                f'@echo off\n'
                f'timeout /t 1 >nul\n'
                f'move /y "{SCRIPT_PATH}.new" "{SCRIPT_PATH}"\n'
                f'start python "{SCRIPT_PATH}"\n'
                f'del "%~f0"'
            )

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


def download_interattivo(L, scelta):
    while True:
        clear_screen()
        print(L['loop_head'])
        u = input(L['loop_prompt']).strip()

        if u.lower() == 'x':
            break

        if not u:
            continue

        opts = {
            'ffmpeg_location': os.path.join(FFMPEG_ROOT, "bin"),
            'outtmpl': os.path.join(MUSIC_DIR if scelta == '1' else VIDEO_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }

        if scelta == '1':
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            })
        else:
            opts.update({
                'format': 'bv*+ba/b',
                'merge_output_format': 'mp4'
            })

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([u])
            mostra_info(L, L['msg_download_ok'])
        except Exception as e:
            log_errore(f"Download fallito per URL: {u}", e)
            mostra_errore(L, L['msg_download_fail'], e)

        pausa(L)


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    init_logger()

    curr = None

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                raw = f.read().strip()

            curr = normalizza_lingua(raw)

            if curr in LANGS:
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    f.write(curr)
        except Exception as e:
            log_errore("Lettura config lingua fallita", e)
            curr = None

    if curr not in LANGS:
        curr = scegli_lingua()

    L = LANGS[curr]

    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)

    if not installa_ffmpeg_auto(L):
        return

    while True:
        clear_screen()
        print("===========================================")
        print("      SUPER DOWNLOADER PRO V2.8")
        print("===========================================")
        for i in range(1, 9):
            print(f" [{i}] -> {L[f'opt{i}']}")
        print("===========================================")

        s = input("> ").strip()

        if s == '8':
            break
        elif s == '7':
            if os.path.exists(CONFIG_FILE):
                try:
                    os.remove(CONFIG_FILE)
                except Exception as e:
                    log_errore("Eliminazione config lingua fallita", e)
            main()
            break
        elif s in ['1', '2']:
            download_interattivo(L, s)
        elif s == '3':
            converti_mkv_a_mp4(L)
        elif s == '4':
            estrai_mp3(L)
        elif s == '5':
            aggiorna_script(L)
        elif s == '6':
            aggiorna_ytdlp(L)
        else:
            mostra_info(L, L['msg_invalid_choice'])
            pausa(L)


if __name__ == "__main__":
    main()
