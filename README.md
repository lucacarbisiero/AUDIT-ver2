# Audit Energetico — fbc group

Applicazione web per **compilare e generare la relazione di un audit energetico**, pronta per la **stampa in PDF**.
Documento tecnico per il reparto IT (deploy, dipendenze, manutenzione).

> Progetto **indipendente** dall'app "Diagnosi Energetica" (cartella `DE-main`): non condividono codice, file o dati.

---

## 1. Tipo di applicazione
- **PWA statica**: solo `HTML + CSS + JavaScript`. **Nessun backend, nessun database server.**
- Tutto risiede in un unico file `index.html` + alcuni file dati/asset locali.
- I dati dei progetti restano **sul dispositivo dell'utente** (`localStorage` del browser).

## 2. Come si esegue / Deploy
- **Uso locale**: aprire `index.html` con un browser (consigliati **Chrome/Edge**).
- **Deploy**: copiare la cartella su un qualsiasi **hosting statico** (IIS, Apache/Nginx, GitHub Pages, SharePoint statico, ecc.). Non serve runtime server-side.
- Per funzionare come **PWA installabile e offline** dev'essere servita via **HTTP/HTTPS** (non da `file://`): in tal caso si registra il service worker `sw.js`.

## 3. Dipendenze esterne (CDN) e comportamento offline
Caricate da CDN al primo avvio (poi messe in cache dal service worker):
- **Chart.js 4.4.1** + **chartjs-plugin-datalabels 2.2.0** (grafici) — `cdn.jsdelivr.net`
- **SheetJS (xlsx) 0.18.5** (import/export Excel) — `cdn.jsdelivr.net`
- **Google Maps** (mappa del sito) — `iframe` con `output=embed`, **senza API key**

Comportamento: dopo la prima apertura online l'app funziona **offline** (grazie a `sw.js`); la **mappa** richiede comunque la rete per visualizzarsi. Senza rete al primo avvio, i grafici/Excel non sono disponibili (il resto sì).

## 4. Dati e privacy
- Salvataggio progetti: `localStorage`, chiave **`audit_projects_v1`**; bozza automatica: **`audit_draft_v1`**.
- Import/Export: **JSON** e **Excel** (file scaricati localmente dall'utente).
- **Nessun dato dell'azienda viene inviato a server fbc/terzi.** Le uniche chiamate esterne sono ai CDN (librerie) e a Google Maps (solo l'indirizzo digitato, per mostrare la mappa).

## 5. Inventario file
**Da pubblicare (necessari al funzionamento):**
| File | Ruolo |
|------|-------|
| `index.html` | Applicazione completa |
| `ateco_map.js` | Dati: descrizioni e benchmark per codice ATECO (`window.ATECO_MAP`) |
| `comuni_gg.js` | Dati: province **attuali**, zona climatica e gradi giorno per comune, DPR 412/93 (`window.PROVINCE_IT`, `window.COMUNI_GG`) |
| `logo.png` | Logo fbc (intestazione relazione) |
| `icona-192.png`, `icona-512.png` | Icone PWA |
| `manifest.json` | Manifesto PWA |
| `sw.js` | Service worker (cache offline) |

**Da NON pubblicare (solo sviluppo — escludere dal deploy):**
- `build_comuni.py`, `make_icons.py` — script di manutenzione/build (vedi §7).
- `README.md` — questo documento.

## 6. Stampa / PDF
Pulsante **"Stampa / Salva PDF"** → dialogo di stampa del browser. Impostazioni consigliate in Chrome:
- Destinazione: **Salva come PDF** · Margini: **Predefiniti**
- **Attivare** "Grafica di sfondo" · **Disattivare** "Intestazioni e piè di pagina" del browser

L'impaginazione (formato A4, intestazione con logo e numero di pagina su ogni foglio) è gestita via CSS di stampa.

## 7. Manutenzione
- **Icone** (`icona-*.png`): rigenerabili con `python make_icons.py` (richiede Python + Pillow).
- **Tabella gradi giorno** (`comuni_gg.js`): rigenerabile con `python build_comuni.py` (richiede solo Python; lo `sqlite3` è incluso). Lo script scarica il dataset open **Italy.Core** (SQLite, auto-aggiornato da ISTAT) ed estrae comuni, **province attuali**, zona climatica e gradi giorno DPR 412/93. Versione dati attuale: **ISTAT 2026.03** (≈ 7.800 comuni, 106 province, incluse Lecco, Lodi, Monza-Brianza, ecc.).
- Dopo aver modificato file cacheabili, **incrementare** la costante `CACHE` in `sw.js` per forzare l'aggiornamento nei browser degli utenti.

## 8. Compatibilità
Browser moderni desktop (Chrome/Edge/Firefox). Interfaccia **ottimizzata desktop**; utilizzabile anche da tablet/smartphone (anteprima a schermo intero).

## 9. Note funzionali (sintesi)
Form dati (azienda, ATECO con benchmark, clima Regione→Provincia→Comune→gradi giorno, consumi annui e mensili, tariffe, aree di intervento, fotovoltaico) → relazione con tabelle, **5 grafici**, KPI/benchmark, CO₂, risparmi con payback, sintesi esecutiva. I **benchmark ENEA** ufficiali (per codice ATECO) sono consultabili tramite il pulsante dedicato che apre `ipedb.enea.it` (richiede registrazione ENEA).

**Impaginazione di stampa**: la relazione è suddivisa in **fogli A4** con intestazione (logo) e **numero di pagina** ("Pag X di N") su ogni foglio. La tabella **"Aree di intervento"**, se lunga, viene **divisa automaticamente su più pagine** (misurazione lato client): le pagine di prosecuzione riportano l'intestazione ripetuta e il titolo "Aree di intervento – segue" (non numerato e non incluso nell'indice).
