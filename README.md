# 🎬 Super Downloader Pro v2.8

Un potente downloader da terminale in Python per scaricare audio e video da internet (YouTube e altri siti supportati da yt-dlp).

---

## 🚀 Funzionalità

- 🎵 Download MP3 (alta qualità 192 kbps)
- 🎬 Download MP4 (video + audio)
- 🔄 Conversione automatica MKV → MP4
- 🎧 Estrazione MP3 da video locali
- 🌍 Supporto multilingua
- ⚡ Download continuo (loop senza riavviare)
- 🔧 Installazione automatica di FFmpeg
- 🔄 Aggiornamento automatico script
- ⬆️ Aggiornamento integrato di yt-dlp
- 📝 Sistema di logging errori

---

## 📁 Struttura cartelle

Il programma crea automaticamente:
C:\FreeSuperDownloader
│
├── Musica\ # File MP3
├── Video\ # File video
├── log.txt # Log errori
└── config.txt # Lingua selezionata

---

## 🧰 Requisiti

- Python 3.x
- Connessione Internet
- Windows (ottimizzato per)

Le dipendenze vengono installate automaticamente:
- `yt-dlp`
- `FFmpeg` (download automatico)

---

## ▶️ Utilizzo

Avvia lo script:

```bash
python FreeSuperDownloader.py

Download MP3 / MP4
Seleziona opzione 1 o 2
Incolla il link
Premi INVIO
Il download parte automaticamente

👉 Modalità continua: inserisci più link senza riavviare
👉 Premi X per tornare al menu
