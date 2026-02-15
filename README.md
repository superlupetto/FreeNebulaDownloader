# SuperDownloader

🚀 Super Downloader Python V1.3

Un potente strumento basato su Python e yt-dlp per scaricare video e musica da YouTube (e oltre 1000 altri siti) alla massima qualità possibile. Sostituisce la vecchia versione .bat con una logica più solida e un'installazione automatizzata.

✨ Caratteristiche

Audio MP3: Estrazione automatica dell'audio a 192kbps.

Video MP4: Download in alta risoluzione (1080p, 2K, 4K) con merge automatico.

Auto-Configurazione: Crea automaticamente le cartelle in C:\Super Downloader.

Auto-FFmpeg: Se FFmpeg non viene trovato in C:\FFmpeg\bin, lo script lo scarica e lo configura da solo.

Sempre Aggiornato: Funzione integrata per aggiornare il "motore" yt-dlp e pip.

📂 Struttura delle Cartelle

Lo script organizza i file in percorsi fissi per evitare confusione:

C:\Super Downloader\Musica -> Per i tuoi file .mp3

C:\Super Downloader\Video -> Per i tuoi file .mp4

C:\FFmpeg\bin -> Sede dei binari necessari per la conversione.

🛠️ Requisiti

Python 3.10+: Scaricabile dal Sito Ufficiale Python o dal Microsoft Store.

yt-dlp: Installabile tramite lo script stesso o con:

