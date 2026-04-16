# FreeSuperDownloader PRO

Downloader e convertitore **MP3 / MP4** con interfaccia grafica (Tkinter) basato su **yt-dlp** e **FFmpeg**.

## Cosa fa

- **Scarica audio (MP3)** o **video (MP4)** da un URL supportato da `yt-dlp`.
- **Coda download**: puoi aggiungere più link e verranno processati in sequenza.
- **Progress** live con percentuale e barra.
- **Auto-install/repair FFmpeg** (Windows): se non presente, lo scarica e lo configura automaticamente.
- **Aggiornamento app** (pulsante Update): sostituisce il file `.pyw` con la versione remota.
- **Aggiornamento yt-dlp** (pulsante yt-dlp): aggiorna il pacchetto via `pip`.

> Nota: questa cartella contiene `FreeSuperDownloader.pyw` (l’app). La logica di download/conversione è tutta lì.

## Requisiti

- **Windows 10/11**
- **Python 3.10+** consigliato (funziona anche con versioni 3.x recenti) (link)[https://www.python.org/ftp/python/pymanager/python-manager-26.1.msix]
- Connessione internet (per download, FFmpeg e update)

Dipendenze Python:

- `yt-dlp` (viene installato automaticamente al primo avvio se mancante)

## Avvio

Doppio click su `FreeSuperDownloader.pyw` oppure da terminale:

```bash
python FreeSuperDownloader.pyw
```

## Uso rapido

1. Scegli il formato con il **toggle animato**:
   - **MP3** (audio)
   - **MP4** (video)
2. Incolla l’URL nel campo.
3. Premi **Download**.

### UX extra

- **Click destro** sul campo URL → menu:
  - **Incolla**
  - **Incolla e avvia**
- **Doppio click** sul campo URL → incolla dagli appunti.
- A fine download: il campo URL viene **svuotato automaticamente**.

## Dove salva i file

L’app crea una cartella in:

- `Documenti\FreeSuperDownloader\`

Sottocartelle:

- `Musica\` → output **MP3**
- `Video\` → output **MP4**
- `ffmpeg\` → installazione locale di FFmpeg (se auto-installata)

Pulsanti rapidi:

- **Apri Musica**
- **Apri Video**

## Come funziona la conversione

- Modalità **MP3**: scarica l’audio migliore e lo converte in MP3 tramite FFmpeg (postprocessor `FFmpegExtractAudio`).
- Modalità **MP4**: scarica best video + audio e merge in MP4 (`merge_output_format = "mp4"`), con flag `+faststart`.

## Update dell’app

Premendo **Update**:

- l’app scarica la versione remota e la salva temporaneamente come `update.py`
- crea `update.bat` che sostituisce il file in esecuzione e riavvia l’app

### Nota importante (404 Not Found)

Gli URL “raw” di GitHub sono **case-sensitive**: il file remoto deve chiamarsi **esattamente**:

- `FreeSuperDownloader.pyw`

Se `version.txt` non esiste nel repo remoto, l’app ricava la versione leggendo `VERSION = "..."` direttamente dal file remoto.

## Update di yt-dlp

Premendo **yt-dlp** l’app esegue:


## FFmpeg (auto repair)

Se FFmpeg non è presente, l’app scarica una build Windows (GPL) e la estrae in:

- `Documenti\FreeSuperDownloader\ffmpeg\bin\ffmpeg.exe`
- `Documenti\FreeSuperDownloader\ffmpeg\bin\ffprobe.exe`

Se vedi errori legati a FFmpeg:

- controlla che la cartella `ffmpeg\bin\` contenga **ffmpeg.exe** e **ffprobe.exe**
- in caso di installazione corrotta, cancella la cartella `ffmpeg\` e riavvia l’app (verrà reinstallato)

## Troubleshooting

- **Download non parte / link non supportato**
  - Non tutti i siti sono supportati da `yt-dlp`.
  - Aggiorna `yt-dlp` col pulsante dedicato.

- **Conversione MP3 fallisce**
  - Verifica che FFmpeg sia installato (l’app prova a ripararlo automaticamente).

- **Percorsi / permessi**
  - L’app scrive in `Documenti\FreeSuperDownloader`. Assicurati di avere permessi di scrittura.

## Sicurezza e note

- L’app scarica contenuti da internet: usa solo link fidati.
- Il pulsante **Update** sostituisce il file in esecuzione: usalo solo se ti fidi della sorgente (repo GitHub indicato nel codice).

## Licenza

Licenza free
