# Parser e indicizzatore di documenti per basi di conoscenza

Motore Python modulare ed estensibile che estrae metadati normalizzati e contenuti testuali da file aziendali eterogenei (`.txt`, `.md`, `.csv`), crea un indice della base di conoscenza in memoria, supporta la ricerca per parola chiave e il calcolo di statistiche riepilogative, e salva l'indice in formato JSON.

## Funzionalità

- **Acquisizione di più formati:** parser inclusi per file di testo (`.txt`), Markdown (`.md`) e CSV tabellari (`.csv`), con rilevamento automatico del delimitatore.
- **Modello canonico unificato:** ogni documento viene normalizzato secondo lo schema `Document` (`doc_id`, `title`, `date`, `word_count`, `preview`, `content`, `format`, `source_path`, `metadata`).
- **Architettura aperta all'estensione:** i parser dei diversi formati derivano da `BaseParser` e vengono registrati in `ParserRegistry`. Per aggiungere un formato basta introdurre una nuova classe e registrarla, senza modificare il flusso esistente.
- **Gestione resiliente degli errori:** i file illeggibili, vuoti, danneggiati o non supportati vengono segnalati e saltati senza interrompere l'elaborazione in batch.
- **Interfaccia da riga di comando (CLI):** comandi per creare indici, cercare parole chiave, filtrare per formato, elencare documenti e consultare statistiche dell'archivio.

## Installazione

Crea un ambiente virtuale e installa il pacchetto:

```bash
python -m venv .venv
source .venv/bin/activate  # Su Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Uso della CLI

### 1. Creare un indice da una cartella di documenti

```bash
python -m kbparser.cli build sample_archive --output knowledge_base.json
```

Il comando mostra un riepilogo dei file elaborati e di quelli saltati, con le relative motivazioni. L'output dell'applicazione è riportato in inglese:

```text
============================================================
PARSING EXECUTION SUMMARY
============================================================
Total files examined:    16
Successfully indexed:    12
Skipped / Failed files:  4
------------------------------------------------------------
DETAILS OF SKIPPED FILES:
 - [UnsupportedFormatError] backup_dump_2026.bak
   Reason: [backup_dump_2026.bak] No parser registered for extension '.bak'
 - [CorruptedFileError] export_corrotto_troncato.csv
   Reason: [export_corrotto_troncato.csv] Corrupted tabular structure: 3 rows have irregular column counts
 - [EmptyFileError] file_vuoto_zero_bytes.txt
   Reason: [file_vuoto_zero_bytes.txt] File is empty (0 bytes)
 - [UnsupportedFormatError] template1.pdf
   Reason: [template1.pdf] No parser registered for extension '.pdf'
------------------------------------------------------------
============================================================
```

### 2. Cercare documenti per parola chiave

```bash
python -m kbparser.cli search knowledge_base.json -q "sicurezza" --preview
```

Opzioni di ricerca:

- `-q, --query`: parola o testo da cercare nel titolo e nel contenuto.
- `-f, --format`: filtra per estensione (`txt`, `md`, `csv`).
- `--preview`: mostra un estratto del documento.
- `--title-only`: cerca soltanto nei titoli.
- `--content-only`: cerca soltanto nel contenuto.

### 3. Consultare le statistiche dell'archivio

```bash
python -m kbparser.cli stats knowledge_base.json
```

### 4. Elencare tutti i documenti indicizzati

```bash
python -m kbparser.cli list knowledge_base.json
```

## API per l'uso da Python

```python
from pathlib import Path
from kbparser.engine import BatchEngine
from kbparser.index import KnowledgeBaseIndex

engine = BatchEngine()
index = KnowledgeBaseIndex()

summary = engine.process_directory(Path("sample_archive"), index=index)
summary.print_report()

# Ricerca
matches = index.search("PostgreSQL")
for doc in matches:
    print(doc.title, doc.format, doc.word_count)

# Salvataggio e caricamento
index.save_to_json(Path("kb.json"))
reloaded = KnowledgeBaseIndex.load_from_json(Path("kb.json"))
```

## Aggiungere nuovi formati

Crea una sottoclasse di `BaseParser` e registrala nel registro:

```python
from pathlib import Path
from typing import ClassVar, Tuple
from kbparser.parsers.base import BaseParser
from kbparser.models import Document

class HtmlParser(BaseParser):
    supported_extensions: ClassVar[Tuple[str, ...]] = ("html", "htm")

    def parse(self, file_path: Path) -> Document:
        raw = self._read_text_safely(file_path)
        # Analizza l'HTML e restituisce un oggetto Document
        ...
```

Puoi registrare il parser in `kbparser.parsers.registry.create_default_registry()` oppure passarlo direttamente a `ParserRegistry().register(HtmlParser)`.

## Eseguire i test

Esegui la suite di test con pytest:

```bash
pytest -v
```

## Note tecniche sul codice
__init__.py è il punto d'ingresso del sottosistema di parsing: presenta i parser e il registro attraverso un'interfaccia ordinata, mentre ogni formato mantiene la propria implementazione in un modulo distinto. Questa organizzazione rende il codice più facile da usare e consente di aggiungere formati con modifiche circoscritte.

BaseParser definisce il contratto comune e raccoglie le funzioni riutilizzabili dai parser di testo, Markdown e CSV. Ogni parser concreto implementa il metodo parse() per leggere il proprio formato e restituire un oggetto Document; può riusare gli strumenti della classe base per leggere i file, ricavare dati e uniformare il contenuto. In questo modo i parser condividono le regole comuni, mentre la logica specifica di ciascun formato resta separata.

ABC significa Abstract Base Class (classe base astratta) e viene importata dal modulo standard Python abc. Scrivere class BaseParser(ABC) marca la classe come base destinata a essere estesa. Insieme a @abstractmethod, impedisce di creare direttamente un BaseParser o una sottoclasse che non abbia implementato parse(). Così il sistema evita di usare un parser incompleto.

@abstractmethod dichiara che parse() è obbligatorio per ogni parser concreto. La base ne specifica parametri, risultato atteso (Document) e possibili errori, ma lascia ai parser di formato il compito di implementare l'elaborazione. Ad esempio, TxtParser, MarkdownParser e CsvParser forniscono la propria versione.

Un metodo decorato con @classmethod riceve come primo argomento la classe (cls), anziché un oggetto già creato (self). can_handle() usa cls.supported_extensions per verificare se l'estensione del percorso è tra quelle dichiarate dal parser. Questo permette di fare il controllo sulla classe, prima ancora di avere un'istanza, e fa sì che il metodo si adatti alle estensioni definite nelle sottoclassi.

Un metodo decorato con @staticmethod non riceve automaticamente né l'istanza (self) né la classe (cls). È una funzione correlata al compito dei parser che non ha bisogno di accedere allo stato di un oggetto. In BaseParser questa scelta si applica, per esempio, a:

_read_text_safely(), legge bytes e prova diverse codifiche, segnalando file vuoti o errori di accesso;

_extract_date(), cerca una data nel testo e la restituisce in forma AAAA-MM-GG;

_generate_doc_id(), produce un identificatore a partire dal percorso;

_normalize_text(), _extract_preview() e _count_words(), forniscono operazioni comuni di pulizia e riepilogo del testo.

_DATE_PATTERNS è una costante privata del modulo, definita come tupla di espressioni regolari compilate con re.compile(). Le espressioni descrivono due ordinamenti di data:

anno-mese-giorno, ad esempio 2025-04-09;
giorno-mese-anno, ad esempio 09/04/2025.
Per separare le parti accettano trattino, barra o punto. _extract_date() prova i pattern nell'ordine in cui sono elencati, prende la data trovata e converte i separatori in trattini. Se l'anno è all'inizio, mantiene l'ordine; se è alla fine, riordina i componenti. Il risultato normalizzato è quindi AAAA-MM-GG, oppure None se non trova una corrispondenza.

I pattern controllano intervalli plausibili per mese e giorno, ma non validano il calendario completo: per esempio, il solo controllo dell'intervallo non esclude ogni data impossibile come il 31 febbraio. Questa funzione individua e normalizza una data candidata, non sostituisce una validazione rigorosa delle date.

Exceptions.py: FileAccessError e altre ereditano  da ParserError per rappresentare un tipo specifico di errore di parsing. Il corpo contiene solo pass perché la classe non aggiunge comportamento o dati propri: il suo nome e la gerarchia di ereditarietà sono già sufficienti per distinguere l’errore.
Questo permette al codice di sollevare errori specifici, ad esempio FileAccessError, e al motore di intercettarli tutti insieme tramite la classe base ParserError, oppure di gestirli separatamente quando serve.