# VICE RECOMPILED

**Una base riproducibile per analizzare, verificare e riprendere pipeline di ricerca console → PC su Windows.**

[Stato](#stato-del-progetto) · [Installazione](#installazione) · [Utilizzo](#utilizzo) · [Come funziona](#come-funziona) · [Roadmap](#roadmap) · [Contribuire](#vuoi-dare-una-mano) · [Licenza](#licenza)

VICE RECOMPILED è un toolkit locale scritto in Python. Esamina una copia già leggibile del pacchetto, una cartella di lavoro e un repository sorgente per produrre prove verificabili sullo stato della pipeline: revisione Git utilizzata, spazio disponibile, pool di texture completati o incompleti, checkpoint audio e shader, presenza dell'eseguibile e regressioni rispetto a un rapporto precedente.

Il progetto **non è ancora un ricompilatore del gioco** e non rende GTA VI giocabile su PC. Il suo obiettivo attuale è costruire una base affidabile, ripetibile e misurabile sulla quale integrare in futuro strumenti di estrazione, traduzione e runtime sviluppati separatamente.

> [!IMPORTANT]
> Questo repository non contiene il gioco, chiavi, shader, modelli, texture, audio o codice eseguibile proprietario. Non decifra pacchetti, non aggira DRM e non spiega come ottenere materiale riservato. I percorsi indicati negli esempi devono puntare esclusivamente a file posseduti e già leggibili dall'utente. I rapporti generati restano sul computer locale e non includono il contenuto dei file analizzati.

## Stato del progetto

| Componente | Stato |
|---|---|
| Rilevamento revisione Git e stato clean/dirty | ✅ Funziona |
| Controllo dello spazio disponibile | ✅ Funziona |
| Mappatura dei package e dei pool `.ttpf` | ✅ Funziona |
| Rilevamento pool completati tramite manifest | ✅ Funziona |
| Checkpoint audio OGG/XMA e indice shader | ✅ Funziona |
| Rapporto leggibile e JSON atomico | ✅ Funziona |
| Lockfile di revisione e toolchain | ✅ Funziona |
| Confronto con baseline e rilevamento regressioni | ✅ Funziona |
| Test automatici con dati sintetici | ✅ 4/4 superati |
| Estrazione o conversione degli asset | ⚠️ Non implementata qui |
| Traduzione degli shader RDNA2 → SPIR-V | ⚠️ Non implementata qui |
| Loader PE e shim delle API Xbox/GDK | ⚠️ Non implementati qui |
| Xbox D3D12 → Vulkan | ⚠️ Non implementato qui |
| Traduzione o ricompilazione dell'eseguibile | ❌ Non disponibile |
| Avvio del gioco o modalità giocabile | ❌ No |

## Installazione

### Requisiti

- Windows 10 o Windows 11 x64;
- Python 3.10 o successivo;
- Git, se si desiderano revisione e stato del repository sorgente;
- una copia personale già leggibile del pacchetto da analizzare;
- una cartella di lavoro prodotta dalla pipeline che si vuole controllare.

Clona il repository:

```powershell
git clone https://github.com/franco00912/VICE-RECOMPILED.git
cd VICE-RECOMPILED
```

Il toolkit usa soltanto la libreria standard di Python: non sono richiesti pacchetti `pip`.

## Utilizzo

Rapporto immediato nel terminale:

```powershell
python vice_recompiled.py `
  --game "D:\path\to\your\readable-package" `
  --work "D:\build-work" `
  --repo "D:\ProjectSource"
```

Scrittura atomica del rapporto e del lockfile:

```powershell
python vice_recompiled.py `
  --game "D:\path\to\your\readable-package" `
  --work "D:\build-work" `
  --repo "D:\ProjectSource" `
  --write-report "D:\build-work\vice-recompiled-status.json" `
  --write-lock "D:\build-work\vice-recompiled.lock.json"
```

Confronto con una misurazione precedente:

```powershell
python vice_recompiled.py `
  --game "D:\path\to\your\readable-package" `
  --work "D:\build-work" `
  --repo "D:\ProjectSource" `
  --baseline "D:\build-work\previous-status.json"
```

Usa `--json` per inviare il rapporto completo allo standard output. Se un pool precedentemente completato risulta regredito, il programma restituisce il codice di uscita `3`, utile in script e sistemi CI.

## Come funziona

| Parte | Cosa controlla |
|---|---|
| Sorgenti | Commit Git, modifiche locali e stato dei sottomoduli |
| Storage | Spazio libero sulle unità che ospitano pacchetto e cartella di lavoro |
| Texture pool | Corrispondenza fra package `.ttpf`, pack secondari e cartelle di output attese |
| Completamento | Presenza dei manifest che attestano la conclusione di ciascun pool |
| Checkpoint | Marker per audio OGG/XMA e indice degli shader tradotti |
| Eseguibile | Segnala soltanto se il file atteso è presente; non lo esegue né lo modifica |
| Riproducibilità | Registra revisione, versione Python e piattaforma in un lockfile locale |
| Regressioni | Confronta due rapporti e individua pool persi o appena completati |

Le scritture dei rapporti sono atomiche: il file temporaneo viene sostituito soltanto quando il nuovo JSON è completo. Il programma legge nomi, marker e metadati necessari alla verifica, ma non incorpora contenuti di gioco nei rapporti.

## Test

```powershell
python -m unittest discover -s tests -v
```

I test usano esclusivamente directory temporanee e dati sintetici. Verificano la mappatura dei pool, il confronto fra rapporti e la scrittura atomica senza includere materiale di gioco.

## Roadmap

I prossimi obiettivi realistici sono:

- aumentare la copertura dei test e aggiungere una workflow CI;
- definire uno schema JSON versionato e validabile;
- aggiungere adattatori opzionali per pipeline esterne senza copiarne il contenuto;
- produrre una dashboard locale dello stato di avanzamento;
- registrare versioni e hash degli strumenti usati in ogni fase;
- mantenere nettamente separati strumenti originali e materiale proprietario dell'utente.

Qualsiasi futuro lavoro su loader, shader, grafica o compatibilità delle API dovrà essere implementato e verificato separatamente. La presenza di un eseguibile non implica che possa essere avviato su Windows.

## Vuoi dare una mano?

Sono benvenuti contributi su test, portabilità, documentazione, schema dei rapporti, logging e integrazione CI. Non allegare mai a issue o pull request file del gioco, asset estratti, shader proprietari, chiavi, eseguibili o rapporti contenenti percorsi personali.

Prima di proporre una modifica:

1. esegui tutti i test;
2. usa fixture sintetiche;
3. descrivi con precisione cosa è stato realmente verificato;
4. evita affermazioni di compatibilità o avvio non dimostrate.

## Confini del progetto

VICE RECOMPILED è un progetto di ricerca indipendente e non è affiliato, approvato o sponsorizzato da Rockstar Games, Take-Two Interactive, Microsoft o dai rispettivi partner. Grand Theft Auto e tutti i nomi correlati appartengono ai rispettivi proprietari.

## Licenza

Il codice originale di VICE RECOMPILED è distribuito con licenza MIT. Consulta [`LICENSE`](LICENSE).
