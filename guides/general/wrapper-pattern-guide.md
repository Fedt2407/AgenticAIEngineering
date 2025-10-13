# Guida ai Wrapper Pattern in Python per Sistemi Agentic AI

## Indice
1. [Introduzione al Concetto di Wrapper](#introduzione)
2. [Wrapper in Python: Definizione e Scopo](#wrapper-in-python)
3. [Caso Studio: GoogleSerperAPIWrapper](#caso-studio)
4. [Vantaggi del Pattern Wrapper](#vantaggi)
5. [Applicazioni nei Sistemi Agentic](#applicazioni-agentic)
6. [Best Practices](#best-practices)

---

## Introduzione al Concetto di Wrapper {#introduzione}

Un **wrapper** (dall'inglese "involucro" o "avvolgitore") è un design pattern fondamentale nella programmazione che consiste nell'avvolgere una funzionalità esistente per fornire un'interfaccia più semplice, standardizzata o arricchita.

### Metafora Pratica
Pensa al wrapper come a un "traduttore simultaneo" che:
- Prende qualcosa di complicato da una parte
- Lo traduce in qualcosa di semplice dall'altra
- Gestisce tutti i dettagli tecnici nel mezzo

### Obiettivi Principali

| Obiettivo | Descrizione |
|-----------|-------------|
| **Semplificazione** | Riduce la complessità di interfacce complicate |
| **Standardizzazione** | Fornisce un'interfaccia uniforme per servizi diversi |
| **Astrazione** | Nasconde dettagli implementativi non necessari |
| **Arricchimento** | Aggiunge funzionalità extra (logging, caching, error handling) |

---

## Wrapper in Python: Definizione e Scopo {#wrapper-in-python}

In Python, un wrapper è tipicamente implementato come una **classe** che:

1. **Incapsula** logica complessa o chiamate a servizi esterni
2. **Espone** metodi pubblici semplificati
3. **Gestisce** configurazioni, autenticazione e dettagli tecnici internamente
4. **Fornisce** error handling e validazione

### Struttura Tipica di un Wrapper

```python
class APIWrapper:
    def __init__(self, api_key=None, config=None):
        """Inizializzazione: carica configurazioni, credenziali, ecc."""
        self.api_key = api_key or os.getenv("API_KEY")
        self.config = config or self._default_config()
        self.client = self._initialize_client()
    
    def run(self, query, **kwargs):
        """Metodo pubblico semplice per l'utente"""
        # Gestisce tutta la complessità internamente
        return self._execute_request(query, **kwargs)
    
    def _execute_request(self, query, **kwargs):
        """Metodi privati per logica interna"""
        # Autenticazione, HTTP request, parsing, error handling
        pass
```

---

## Caso Studio: GoogleSerperAPIWrapper {#caso-studio}

### Esempio Pratico da LangChain

```python
from langchain_community.utilities import GoogleSerperAPIWrapper

# Inizializzazione semplice
serper = GoogleSerperAPIWrapper()

# Utilizzo immediato
result = serper.run("What is the capital of France?")
```

### Cosa Succede Dietro le Quinte

#### ❌ SENZA Wrapper (Implementazione Manuale)

```python
import requests
import os
import json

# 1. Recupero credenziali
api_key = os.getenv("SERPER_API_KEY")
if not api_key:
    raise ValueError("API key mancante!")

# 2. Configurazione headers
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

# 3. Preparazione richiesta
url = "https://google.serper.dev/search"
payload = {
    "q": "What is the capital of France?",
    "num": 10  # numero risultati
}

# 4. Gestione richiesta HTTP
try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
except requests.Timeout:
    print("Timeout della richiesta")
except requests.HTTPError as e:
    print(f"Errore HTTP: {e}")

# 5. Parsing risposta
try:
    data = response.json()
except json.JSONDecodeError:
    print("Errore nel parsing JSON")

# 6. Estrazione informazioni rilevanti
results = []
for item in data.get("organic", []):
    results.append({
        "title": item.get("title"),
        "snippet": item.get("snippet"),
        "link": item.get("link")
    })

# 7. Formattazione output finale
formatted_output = "\n\n".join([
    f"{r['title']}\n{r['snippet']}\n{r['link']}" 
    for r in results
])
```

#### ✅ CON Wrapper (Implementazione Semplificata)

```python
from langchain_community.utilities import GoogleSerperAPIWrapper

serper = GoogleSerperAPIWrapper()
result = serper.run("What is the capital of France?")

# Tutto gestito automaticamente! ✨
```

### Funzionalità Gestite Automaticamente dal Wrapper

1. **Autenticazione**
   - Legge automaticamente `SERPER_API_KEY` dalle variabili d'ambiente
   - Gestisce diversi metodi di autenticazione

2. **HTTP Request Management**
   - Costruisce headers corretti
   - Configura timeout appropriati
   - Gestisce retry logic in caso di errori temporanei

3. **Error Handling Robusto**
   - Gestisce timeout di rete
   - Intercetta errori HTTP (4xx, 5xx)
   - Gestisce rate limiting
   - Fornisce messaggi d'errore significativi

4. **Parsing Intelligente**
   - Converte JSON in strutture Python
   - Estrae informazioni rilevanti
   - Gestisce formati di risposta variabili

5. **Formattazione Output**
   - Restituisce dati in formato consistente
   - Compatibile con altri componenti LangChain
   - Pronto per uso in chain e agent

6. **Configurabilità**
   - Parametri opzionali per personalizzazione
   - Defaults sensati out-of-the-box
   - Estendibile per casi d'uso specifici

---

## Vantaggi del Pattern Wrapper {#vantaggi}

### 1. Riduzione della Complessità
- **Da**: 50+ righe di codice boilerplate
- **A**: 2 righe di codice funzionale

### 2. Manutenibilità
```python
# Se l'API Serper cambia, aggiorni solo il wrapper
# Il tuo codice rimane identico
serper = GoogleSerperAPIWrapper()  # versione 1.0
serper = GoogleSerperAPIWrapper()  # versione 2.0 - stesso codice!
```

### 3. Testabilità
```python
# Facile creare mock per testing
class MockSerperWrapper:
    def run(self, query):
        return "Mocked response"

# Nei test usi il mock, in produzione usi quello vero
```

### 4. Riusabilità
```python
# Usa lo stesso wrapper in progetti diversi
# Nessun codice duplicato
```

### 5. Standardizzazione
```python
# Interfaccia uniforme per servizi diversi
serper = GoogleSerperAPIWrapper()
wiki = WikipediaAPIWrapper()
wolfram = WolframAlphaAPIWrapper()

# Tutti hanno lo stesso metodo .run()
serper.run("query")
wiki.run("query")
wolfram.run("query")
```

---

## Applicazioni nei Sistemi Agentic {#applicazioni-agentic}

### Integrazione in LangGraph e CrewAI

I wrapper sono fondamentali nei sistemi agentic perché permettono agli agent di utilizzare **tools** in modo uniforme.

#### Esempio: Tool Configuration in LangGraph

```python
from langchain_community.utilities import (
    GoogleSerperAPIWrapper,
    WikipediaAPIWrapper,
    WolframAlphaAPIWrapper
)
from langchain.tools import Tool

# Crea wrapper per servizi diversi
serper = GoogleSerperAPIWrapper()
wiki = WikipediaAPIWrapper()
wolfram = WolframAlphaAPIWrapper()

# Definisci tools con interfaccia uniforme
tools = [
    Tool(
        name="search",
        description="Cerca informazioni su internet",
        func=serper.run
    ),
    Tool(
        name="wikipedia",
        description="Cerca su Wikipedia",
        func=wiki.run
    ),
    Tool(
        name="calculator",
        description="Calcoli matematici complessi",
        func=wolfram.run
    )
]

# L'agent può usare qualsiasi tool senza conoscere i dettagli
# Stesso pattern .run() per tutti!
```

#### Vantaggi per gli Agent

1. **Intercambiabilità**: L'agent può cambiare tool senza modifiche al codice
2. **Scalabilità**: Aggiungi nuovi tool facilmente
3. **Manutenibilità**: Aggiorna implementazioni senza toccare la logica dell'agent
4. **Testing**: Testa agent con mock tools

### Pattern nei Principali Framework

| Framework | Utilizzo Wrapper |
|-----------|------------------|
| **LangChain** | Utilities per API esterne (Serper, Wikipedia, ecc.) |
| **CrewAI** | Tool wrappers per orchestrazione multi-agent |
| **LangGraph** | State management e workflow abstractions |
| **OpenAI SDK** | Client wrapper per REST API |

---

## Best Practices {#best-practices}

### 1. Design dell'Interfaccia

```python
# ✅ BUONO: Interfaccia chiara e consistente
class MyAPIWrapper:
    def run(self, query: str, **kwargs) -> str:
        """Esegui una query. Restituisce risultati formattati."""
        pass

# ❌ CATTIVO: Metodi inconsistenti
class MyAPIWrapper:
    def execute_search(self, q):  # Nome diverso
        pass
    
    def get_results(self, query_string):  # Altro nome
        pass
```

### 2. Gestione degli Errori

```python
# ✅ BUONO: Errori specifici e informativi
class MyAPIWrapper:
    def run(self, query):
        try:
            return self._execute(query)
        except AuthenticationError:
            raise ValueError("API key non valida o mancante")
        except RateLimitError:
            raise ValueError("Rate limit raggiunto. Riprova più tardi")
        except Exception as e:
            raise RuntimeError(f"Errore inaspettato: {str(e)}")

# ❌ CATTIVO: Errori generici
class MyAPIWrapper:
    def run(self, query):
        try:
            return self._execute(query)
        except:  # Troppo generico
            print("Errore")  # Non informativo
            return None  # Nasconde il problema
```

### 3. Configurazione

```python
# ✅ BUONO: Configurazione flessibile con defaults sensati
class MyAPIWrapper:
    def __init__(
        self,
        api_key: str = None,
        timeout: int = 10,
        max_retries: int = 3
    ):
        self.api_key = api_key or os.getenv("MY_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries

# ❌ CATTIVO: Configurazione rigida
class MyAPIWrapper:
    def __init__(self, api_key):  # api_key obbligatoria
        self.api_key = api_key
        self.timeout = 5  # Hardcoded, non modificabile
```

### 4. Documentazione

```python
class MyAPIWrapper:
    """
    Wrapper per My API Service.
    
    Fornisce interfaccia semplificata per ricerche web.
    Gestisce automaticamente autenticazione, retry e parsing.
    
    Attributes:
        api_key (str): Chiave API (default: variabile d'ambiente MY_API_KEY)
        timeout (int): Timeout richieste in secondi (default: 10)
    
    Example:
        >>> wrapper = MyAPIWrapper()
        >>> result = wrapper.run("python tutorial")
        >>> print(result)
    """
    
    def run(self, query: str, num_results: int = 10) -> str:
        """
        Esegui una ricerca.
        
        Args:
            query: Stringa di ricerca
            num_results: Numero massimo di risultati (default: 10)
        
        Returns:
            Risultati formattati come stringa
            
        Raises:
            ValueError: Se api_key non è configurata
            RuntimeError: Per errori di rete o API
        """
        pass
```

### 5. Testing

```python
# Crea mock wrapper per testing
class MockAPIWrapper:
    def run(self, query):
        return f"Mock results for: {query}"

# Usa dependency injection
def my_agent(api_wrapper):
    result = api_wrapper.run("test query")
    return result

# In produzione
agent = my_agent(GoogleSerperAPIWrapper())

# Nei test
agent = my_agent(MockAPIWrapper())
```

---

## Conclusione

Il pattern wrapper è fondamentale nello sviluppo di sistemi agentic AI perché:

- **Semplifica** l'integrazione di servizi esterni
- **Standardizza** interfacce diverse in un formato uniforme
- **Facilita** testing, manutenzione e scalabilità
- **Permette** agli agent di concentrarsi sulla logica decisionale invece che sui dettagli tecnici

Comprendere questo pattern è essenziale per lavorare efficacemente con LangChain, LangGraph, CrewAI e altri framework per sistemi agentic.

---

## Riferimenti Utili

- [LangChain Documentation - Utilities](https://python.langchain.com/docs/integrations/tools/)
- [Design Patterns in Python](https://refactoring.guru/design-patterns/python)
- [Serper API Documentation](https://serper.dev/)