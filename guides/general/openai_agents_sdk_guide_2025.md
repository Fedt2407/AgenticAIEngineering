# Guida OpenAI Agents SDK 2025: Agent, Tracing e Runner

## Introduzione

L'OpenAI Agents SDK (settembre 2025) rappresenta l'evoluzione più recente per la creazione di agenti AI produttivi. Questa guida si concentra sui tre pilastri fondamentali: creazione di Agent, utilizzo del tracing per monitoraggio e debugging, e esecuzione tramite Runner.

## 1. Creazione di un'Istanza di Agent

### Introduzione Teorica

La classe `Agent` nell'OpenAI Agents SDK 2025 è il componente centrale che definisce il comportamento, le capacità e la personalità del tuo agente AI. Un Agent incapsula:

- **Identità**: Nome e istruzioni che definiscono il ruolo dell'agente
- **Modello**: Il modello LLM sottostante (GPT-4, GPT-4o, etc.)
- **Strumenti**: Funzioni che l'agente può utilizzare per interagire con il mondo esterno
- **Contesto**: Informazioni stateful che persistono durante le interazioni
- **Output**: Tipo di risposta strutturata che l'agente deve produrre
- **Guardrails**: Regole di sicurezza e validazione

### Setup e Installazione

```python
# Installa l'SDK più recente
# pip install openai-agents

import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from agents import Agent, Runner, trace
from agents.tools import tool
import datetime
import json

# Configura le variabili d'ambiente
# export OPENAI_API_KEY="sk-your-api-key"
```

### Definizione di Strumenti per l'Agent

```python
# Il decoratore @tool è l'evoluzione di @function_tool nell'SDK 2025
# Principali differenze:
# - @tool supporta nativamente funzioni async/await
# - @tool ha una validazione dei tipi più robusta
# - @tool integra automaticamente il tracing
# - @tool supporta più formati di output (non solo JSON)
@tool
async def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Ottieni le informazioni meteo attuali per una località specifica.

    Args:
        location: La città per cui ottenere il meteo (es. "Milano, IT")
        unit: Unità di temperatura ("celsius" o "fahrenheit")

    Returns:
        Informazioni meteo in formato JSON string
    """
    # Simula una chiamata API esterna
    # In produzione, qui chiameresti un servizio meteo reale
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "Soleggiato",
        "humidity": "65%",
        "timestamp": datetime.datetime.now().isoformat()
    }

    # json.dumps ritorna i dati in un formato JSON strutturato
    return json.dumps(weather_data, ensure_ascii=False)

@tool
async def search_web(query: str, max_results: int = 5) -> str:
    """
    Simula una ricerca web per ottenere informazioni aggiornate.

    Args:
        query: La query di ricerca
        max_results: Numero massimo di risultati da restituire

    Returns:
        Risultati di ricerca in formato JSON
    """
    # In produzione, qui integreresti un servizio di ricerca reale
    search_results = {
        "query": query,
        "results": [
            {
                "title": f"Risultato {i+1} per '{query}'",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"Informazioni rilevanti su {query} - risultato {i+1}"
            }
            for i in range(min(max_results, 3))
        ],
        "total_results": max_results
    }

    # json.dumps ritorna i dati in un formato JSON strutturato
    return json.dumps(search_results, ensure_ascii=False)

@tool
async def calculate_math(expression: str) -> str:
    """
    Calcola espressioni matematiche semplici in modo sicuro.

    Args:
        expression: L'espressione matematica da calcolare (es. "2 + 2 * 3")

    Returns:
        Il risultato del calcolo
    """
    try:
        # Esempio 4: Multi-agent coordination definita più in basso nel codice
        print("\n4️⃣ Coordinazione Multi-Agente")
        await multi_agent_runner_example()

        # Esempio 5: Demo comprensiva definita più in basso nel codice
        print("\n5️⃣ Demo Comprensiva")
        await comprehensive_example()

        print("\n✅ Tutti gli esempi completati con successo!")

    except Exception as e:
        print(f"\n❌ Errore nell'esecuzione degli esempi: {str(e)}")
        raise

# Per eseguire gli esempi, decommenta la riga seguente:
# asyncio.run(main())
```

## Best Practices e Considerazioni Avanzate

### 1. Gestione degli Errori e Resilienza

```python
from agents.exceptions import MaxTurnsExceeded, ToolExecutionError, AgentError

async def resilient_agent_execution(agent: Agent, user_input: str, max_retries: int = 3):
    """
    Esegue un agente AI in modo resiliente con gestione avanzata degli errori e retry automatici.

    Questa funzione implementa diversi meccanismi di resilienza:
    - Retry automatico con backoff esponenziale
    - Timeout progressivo che aumenta ad ogni tentativo
    - Tracciamento dettagliato dell'esecuzione
    - Gestione specifica per diversi tipi di errori (MaxTurnsExceeded, ToolExecutionError)

    Args:
        agent (Agent): L'istanza dell'agente AI da eseguire
        user_input (str): L'input dell'utente da processare
        max_retries (int, optional): Numero massimo di tentativi di retry. Default 3.

    Returns:
        Il risultato dell'esecuzione dell'agente se ha successo

    Raises:
        MaxTurnsExceeded: Se l'agente supera il limite di turni in tutti i tentativi
        ToolExecutionError: Se fallisce l'esecuzione di uno strumento in tutti i tentativi
        Exception: Per altri errori generici non gestiti dopo tutti i tentativi
    """

    # with trace permette di tracciare il comportamentoe dell'agente nei log disponibili sul sito di OpenAI
    with trace(name="resilient_execution") as exec_trace:
        exec_trace.set_attribute("max_retries", max_retries)
        exec_trace.set_attribute("user_input", user_input)

        for attempt in range(max_retries + 1):
            with exec_trace.span(f"attempt_{attempt + 1}") as attempt_span:
                attempt_span.set_attribute("attempt_number", attempt + 1)

                try:
                    # Configura timeout progressivo (aumenta ad ogni tentativo)
                    timeout = 30 + (attempt * 15)  # 30s, 45s, 60s, 75s
                    attempt_span.set_attribute("timeout_seconds", timeout)

                    result = await Runner.run(
                        agent=agent,
                        input=user_input,
                        max_turns=10 + (attempt * 5),  # Aumenta i turni disponibili
                        timeout=timeout
                    )

                    # Successo - registra e restituisci
                    attempt_span.set_attribute("success", True)
                    exec_trace.set_attribute("successful_attempt", attempt + 1)
                    exec_trace.log(f"Esecuzione riuscita al tentativo {attempt + 1}", level="info")

                    return result

                except MaxTurnsExceeded as e:
                    # L'agente ha superato il limite di turni
                    attempt_span.log(f"Limite turni superato: {str(e)}", level="warning")
                    attempt_span.set_attribute("error_type", "max_turns_exceeded")

                    if attempt == max_retries:
                        # Se abbiamo esaurito tutti i tentativi di retry,
                        # logghiamo l'errore finale e risolleviamo (raise) l'eccezione MaxTurnsExceeded
                        # originale (e) per propagarla al chiamante, permettendo la gestione
                        # dell'errore ai livelli superiori
                        exec_trace.log("Tutti i tentativi falliti per limite turni", level="error")
                        raise

                except ToolExecutionError as e:
                    # Errore nell'esecuzione di uno strumento
                    attempt_span.log(f"Errore strumento: {str(e)}", level="warning")
                    attempt_span.set_attribute("error_type", "tool_execution_error")
                    attempt_span.set_attribute("failed_tool", getattr(e, 'tool_name', 'unknown'))

                    if attempt == max_retries:
                        exec_trace.log("Tutti i tentativi falliti per errori strumenti", level="error")
                        raise

                except Exception as e:
                    # Altri errori generici
                    attempt_span.log(f"Errore generico: {str(e)}", level="warning")
                    attempt_span.set_attribute("error_type", "generic_error")

                    if attempt == max_retries:
                        exec_trace.log("Tutti i tentativi falliti per errori generici", level="error")
                        raise

                # Pausa tra i tentativi (backoff esponenziale)
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    attempt_span.log(f"Attendendo {wait_time}s prima del prossimo tentativo", level="info")
                    await asyncio.sleep(wait_time)

async def circuit_breaker_pattern():
    """
    Implementa un pattern Circuit Breaker per gestire chiamate a servizi esterni in modo resiliente.

    Il Circuit Breaker protegge il sistema da fallimenti a cascata monitorando gli errori e
    interrompendo temporaneamente le chiamate quando viene superata una soglia di fallimenti.

    Caratteristiche principali:
    - Tre stati: CLOSED (normale), OPEN (bloccato), HALF-OPEN (test ripristino)
    - Conteggio fallimenti con soglia configurabile
    - Timeout di reset automatico per tentare il ripristino
    - Monitoraggio e logging dello stato del circuito

    Returns:
        Il risultato dell'operazione se ha successo, altrimenti solleva un'eccezione
    """
    class CircuitBreaker:
        def __init__(self, failure_threshold=5, reset_timeout=60):
            self.failure_threshold = failure_threshold   # Soglia di fallimenti
            self.reset_timeout = reset_timeout           # Tempo prima di riprovare
            self.failure_count = 0                       # Contatore fallimenti
            self.last_failure_time = None                # Timestamp ultimo fallimento
            self.state = "CLOSED"                        # CLOSED, OPEN, HALF_OPEN

        async def call(self, agent, user_input):
            """Esegue la chiamata tramite il circuit breaker."""

            # Se il circuito è aperto, verifica se è ora di riprovare
            if self.state == "OPEN":
                if (datetime.datetime.now() - self.last_failure_time).seconds > self.reset_timeout:
                    self.state = "HALF_OPEN"
                    print("🔄 Circuit breaker: tentativo di ripristino")
                else:
                    raise Exception("Circuit breaker OPEN - servizio temporaneamente non disponibile")

            try:
                # Esegui l'operazione
                result = await Runner.run(agent, user_input)

                # Successo - resetta il contatore se eravamo in HALF_OPEN
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    print("✅ Circuit breaker: servizio ripristinato")

                return result

            except Exception as e:
                # Fallimento - incrementa contatore
                self.failure_count += 1
                self.last_failure_time = datetime.datetime.now()

                # Se superiamo la soglia, apri il circuito
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    print(f"🚫 Circuit breaker OPEN dopo {self.failure_count} fallimenti")

                raise

    # Esempio di utilizzo del circuit breaker
    agent = create_intelligent_assistant()
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30)

    with trace(name="circuit_breaker_demo") as cb_trace:
        try:
            result = await breaker.call(agent, "Test del circuit breaker")
            cb_trace.log("Chiamata riuscita tramite circuit breaker", level="info")
            return result
        except Exception as e:
            cb_trace.log(f"Circuit breaker ha bloccato la chiamata: {str(e)}", level="warning")
            raise
```

### 2. Monitoraggio delle Performance e Metriche

```python
from dataclasses import dataclass
from typing import Dict, List
import time

# Il decoratore @dataclass è un'utilità introdotta in Python 3.7 che automatizza:
# - La creazione del metodo __init__ per inizializzare gli attributi della classe
# - L'implementazione di __repr__ per una rappresentazione leggibile dell'oggetto
# - L'implementazione di __eq__ per confrontare oggetti della classe
# - Altri metodi speciali come __hash__ se richiesto
# Senza @dataclass dovremmo scrivere manualmente tutti questi metodi
# Con @dataclass il codice è più conciso e meno soggetto a errori
@dataclass
class PerformanceMetrics:
    """Classe per raccogliere metriche di performance dettagliate."""
    # Gli attributi vengono dichiarati con type hints e valori di default
    # Python userà questi per generare automaticamente __init__
    execution_time: float = 0.0              # Tempo totale di esecuzione
    llm_calls: int = 0                       # Numero di chiamate LLM
    tool_calls: int = 0                      # Numero di chiamate strumenti
    tokens_used: int = 0                     # Token totali utilizzati
    memory_usage: float = 0.0                # Utilizzo memoria (MB)
    turn_count: int = 0                      # Numero di turni
    # Non possiamo usare errors_encountered: List[str] = [] direttamente perché
    # le liste sono oggetti mutabili e verrebbero condivise tra tutte le istanze della classe.
    # Questo porterebbe a comportamenti indesiderati dove modificare la lista in un'istanza
    # modificherebbe la lista in tutte le altre istanze.
    # Usando None come default e inizializzando una nuova lista in __post_init__,
    # ogni istanza ottiene la sua lista indipendente.
    errors_encountered: List[str] = None     # Lista degli errori

    # __post_init__ è un metodo speciale che viene chiamato dopo __init__
    # Utile per inizializzazioni che richiedono logica aggiuntiva
    def __post_init__(self):
        # Inizializza la lista degli errori se None
        if self.errors_encountered is None:
            self.errors_encountered = []

class PerformanceMonitor:
    """Monitor per raccogliere e analizzare metriche di performance."""

    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []

    async def monitored_execution(self, agent: Agent, user_input: str) -> tuple:
        """
        Esegue l'agente raccogliendo metriche dettagliate di performance.

        Returns:
            Tuple[result, PerformanceMetrics]: Il risultato e le metriche raccolte
        """
        metrics = PerformanceMetrics()

        with trace(name="performance_monitored_execution") as perf_trace:
            # Inizializza contatori
            start_time = time.time()

            import psutil

            # psutil (Python System and Process Utilities) è una libreria cross-platform per recuperare informazioni
            # sui processi in esecuzione e sull'utilizzo delle risorse di sistema (CPU, memoria, dischi, rete, sensori)
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB

            perf_trace.set_attribute("start_memory_mb", start_memory)
            perf_trace.log("Avvio monitoraggio performance", level="info")

            try:
                # Crea uno span (segmento temporale tracciato) per monitorare l'esecuzione dell'agente
                # Lo span è un intervallo di tempo tracciabile che può contenere eventi e metriche
                # Utile per analizzare le performance di specifiche sezioni di codice
                with perf_trace.span("agent_execution_monitored") as exec_span:

                    # Hook per tracciare chiamate LLM
                    original_completion = agent._client.chat.completions.create

                    async def tracked_completion(*args, **kwargs):
                        metrics.llm_calls += 1
                        exec_span.add_event("llm_call", {"call_number": metrics.llm_calls})

                        result = await original_completion(*args, **kwargs)

                        # Traccia utilizzo token se disponibile
                        if hasattr(result, 'usage') and result.usage:
                            tokens = result.usage.total_tokens
                            metrics.tokens_used += tokens
                            exec_span.add_event("tokens_used", {"tokens": tokens})

                        return result

                    # Applica l'hook temporaneamente
                    agent._client.chat.completions.create = tracked_completion

                    # Esegui l'agente
                    result = await Runner.run(agent, user_input)

                    # Ripristina il metodo originale
                    agent._client.chat.completions.create = original_completion

                # Calcola metriche finali
                end_time = time.time()
                end_memory = process.memory_info().rss / 1024 / 1024

                metrics.execution_time = end_time - start_time
                metrics.memory_usage = end_memory - start_memory
                metrics.turn_count = getattr(result, 'turn_count', 0)

                # Conta tool calls dal risultato
                if hasattr(result, 'tool_calls'):
                    metrics.tool_calls = len(result.tool_calls)

                # Registra metriche nella trace
                perf_trace.set_attribute("execution_time", metrics.execution_time)
                perf_trace.set_attribute("llm_calls", metrics.llm_calls)
                perf_trace.set_attribute("tool_calls", metrics.tool_calls)
                perf_trace.set_attribute("tokens_used", metrics.tokens_used)
                perf_trace.set_attribute("memory_delta_mb", metrics.memory_usage)
                perf_trace.set_attribute("turn_count", metrics.turn_count)

                perf_trace.log("Monitoraggio performance completato", level="info")

                # Salva nella cronologia
                self.metrics_history.append(metrics)

                return result, metrics

            except Exception as e:
                metrics.errors_encountered.append(str(e))
                perf_trace.log(f"Errore durante monitoraggio: {str(e)}", level="error")
                raise

    def get_performance_summary(self) -> Dict:
        """Restituisce un riassunto delle performance basato sulla cronologia."""
        if not self.metrics_history:
            return {"message": "Nessuna metrica disponibile"}

        # Calcola statistiche aggregate
        execution_times = [m.execution_time for m in self.metrics_history]
        llm_calls = [m.llm_calls for m in self.metrics_history]
        tokens_used = [m.tokens_used for m in self.metrics_history]

        summary = {
            "total_executions": len(self.metrics_history),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
            "avg_llm_calls": sum(llm_calls) / len(llm_calls),
            "total_tokens_used": sum(tokens_used),
            "avg_tokens_per_execution": sum(tokens_used) / len(tokens_used) if tokens_used else 0,
            "error_rate": len([m for m in self.metrics_history if m.errors_encountered]) / len(self.metrics_history)
        }

        return summary

# Esempio di utilizzo del monitoraggio
async def performance_monitoring_example():
    """Dimostra l'utilizzo del sistema di monitoraggio delle performance."""

    monitor = PerformanceMonitor()
    agent = create_intelligent_assistant()

    print("📊 Avvio test di performance...")

    # Test con query di diversa complessità
    test_queries = [
        "Ciao, come stai?",
        "Calcola 15 + 27 * 3",
        "Che tempo fa a Milano e calcola l'area di un quadrato di lato 8 metri",
        "Fai una ricerca su 'intelligenza artificiale 2025' e riassumi i primi 3 risultati"
    ]

    with trace(name="performance_benchmark") as bench_trace:
        bench_trace.set_attribute("test_queries_count", len(test_queries))

        for i, query in enumerate(test_queries, 1):
            with bench_trace.span(f"query_{i}") as query_span:
                query_span.set_attribute("query", query)
                query_span.set_attribute("query_complexity", len(query.split()))

                print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")

                try:
                    result, metrics = await monitor.monitored_execution(agent, query)

                    print(f"   ⏱️  Tempo: {metrics.execution_time:.2f}s")
                    print(f"   🤖 Chiamate LLM: {metrics.llm_calls}")
                    print(f"   🔧 Chiamate strumenti: {metrics.tool_calls}")
                    print(f"   🎯 Token utilizzati: {metrics.tokens_used}")
                    print(f"   💾 Memoria: {metrics.memory_usage:.1f}MB")

                    query_span.set_attribute("success", True)

                except Exception as e:
                    print(f"   ❌ Errore: {str(e)}")
                    query_span.set_attribute("success", False)
                    query_span.set_attribute("error", str(e))

        # Mostra riassunto finale
        summary = monitor.get_performance_summary()

        print(f"\n📈 Riassunto Performance:")
        print(f"   Esecuzioni totali: {summary['total_executions']}")
        print(f"   Tempo medio: {summary['avg_execution_time']:.2f}s")
        print(f"   Tempo max: {summary['max_execution_time']:.2f}s")
        print(f"   Chiamate LLM medie: {summary['avg_llm_calls']:.1f}")
        print(f"   Token totali: {summary['total_tokens_used']}")
        print(f"   Tasso errori: {summary['error_rate']:.1%}")

        bench_trace.set_attribute("benchmark_summary", summary)

    return summary

# Esempio finale di integrazione completa
async def production_ready_example():
    """
    Esempio pronto per produzione che combina tutti i pattern:
    resilienza, monitoraggio, tracing avanzato.
    """

    print("🏭 Avvio esempio production-ready")

    # Setup componenti
    monitor = PerformanceMonitor()
    agent = create_intelligent_assistant()

    # Query utente simulata
    user_query = "Analizza il mercato delle criptovalute oggi e calcola il rendimento di un investimento di 1000€ al 5% annuo per 10 anni"

    with trace(
        name="production_agent_execution",
        metadata={
            "environment": "production",
            "user_id": "user_12345",
            "session_id": "session_abc789",
            "query_category": "financial_analysis"
        }
    ) as prod_trace:

        prod_trace.log("Avvio esecuzione production", level="info")
        prod_trace.set_attribute("user_query", user_query)

        try:
            # Esecuzione con resilienza e monitoraggio
            with prod_trace.span("resilient_monitored_execution") as exec_span:
                exec_span.log("Combinando resilienza e monitoraggio", level="info")

                # Wrapper che combina resilienza e monitoraggio
                async def resilient_monitored_run(agent, query):
                    for attempt in range(3):  # Max 3 tentativi
                        try:
                            return await monitor.monitored_execution(agent, query)
                        except Exception as e:
                            if attempt == 2:  # Ultimo tentativo (in range va da 0 a 2)
                                raise
                            await asyncio.sleep(2 ** attempt)  # Backoff exponential

                result, metrics = await resilient_monitored_run(agent, user_query)

                exec_span.set_attribute("final_success", True)
                exec_span.set_attribute("execution_metrics", {
                    "time": metrics.execution_time,
                    "llm_calls": metrics.llm_calls,
                    "tokens": metrics.tokens_used
                })

            # Log risultato finale
            prod_trace.log("Esecuzione production completata con successo", level="info")

            print(f"🎉 Risultato finale:")
            print(f"   {result.final_output[:200]}...")
            print(f"\n📊 Metriche:")
            print(f"   Tempo: {metrics.execution_time:.2f}s")
            print(f"   Token: {metrics.tokens_used}")
            print(f"   Chiamate LLM: {metrics.llm_calls}")

            return {
                "result": result,
                "metrics": metrics,
                "success": True
            }

        except Exception as e:
            prod_trace.log(f"Esecuzione production fallita: {str(e)}", level="error")
            prod_trace.set_status("error", str(e))

            print(f"❌ Esecuzione fallita: {str(e)}")

            return {
                "result": None,
                "metrics": None,
                "success": False,
                "error": str(e)
            }

# Per eseguire l'esempio production-ready:
# asyncio.run(production_ready_example())
```

## Conclusioni

Questa guida copre i tre pilastri essenziali dell'OpenAI Agents SDK 2025:

### 🤖 **Agent Creation**

- Configurazione completa con istruzioni, strumenti e contesto
- Agenti specializzati per domini specifici
- Gestione del contesto persistente tra interazioni

### 🔍 **Tracing con trace()**

- Monitoraggio completo del flusso di esecuzione
- Debug avanzato con span personalizzati
- Integrazione con servizi esterni (Logfire, AgentOps)
- Metriche dettagliate e logging strutturato

### 🚀 **Execution con Runner.run**

- Esecuzione robusta con gestione errori
- Configurazione avanzata (timeout, parallelizzazione)
- Coordinazione multi-agente
- Pattern production-ready con resilienza

### 🛡️ **Best Practices**

- Circuit breaker per stabilità
- Monitoraggio performance automatico
- Gestione errori con retry intelligente
- Metriche aggregate per ottimizzazione

Questi pattern ti permetteranno di costruire agenti AI robusti, osservabili e scalabili per applicazioni production-ready nel 2025. Usa eval in modo sicuro solo per operazioni matematiche base

```
allowed_chars = set('0123456789+-\*/.()')
if all(c in allowed_chars or c.isspace() for c in expression):
    result = eval(expression)
    return f"Il risultato di '{expression}' è: {result}"
else:
    return f"Errore: espressione non sicura '{expression}'"
except Exception as e:
    return f"Errore nel calcolo: {str(e)}"

```

### Definizione del Contesto dell'Agent

```python
@dataclass
class AgentContext:
    """
    Contesto persistente che l'agente mantiene durante le interazioni.
    Questo oggetto viene passato tra le chiamate e può contenere
    informazioni sullo stato, preferenze utente, cronologia, etc.
    """
    user_name: str = "Utente"           # Nome dell'utente corrente
    session_id: str = ""                # ID univoco della sessione
    interaction_count: int = 0          # Numero di interazioni nella sessione
    user_preferences: Dict[str, Any] = None  # Preferenze utente personalizzate
    conversation_history: List[str] = None   # Cronologia delle conversazioni

    # È necessario inizializzare i campi mutabili identificati nel blocco con @dataclass con None usando __post_init__
    def __post_init__(self):
        """Inizializza i campi mutabili dopo la creazione dell'oggetto."""
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.conversation_history is None:
            self.conversation_history = []

    def update_interaction_count(self):
        """Incrementa il contatore delle interazioni."""
        self.interaction_count += 1

    def add_to_history(self, message: str):
        """Aggiunge un messaggio alla cronologia."""
        self.conversation_history.append(message)
        # Mantieni solo gli ultimi 10 messaggi per evitare overflow
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
```

### Creazione dell'Agent

```python
def create_intelligent_assistant() -> Agent[AgentContext]:
    """
    Crea un'istanza di Agent intelligente con capacità multiple.

    Returns:
        Agent configurato e pronto all'uso
    """

    # Definisci le istruzioni di sistema per l'agente
    instructions = """
    Sei un assistente AI intelligente e versatile chiamato "IntelliBot".

    Le tue caratteristiche principali:
    - Sei cordiale, professionale e sempre disponibile ad aiutare
    - Puoi utilizzare strumenti per ottenere informazioni aggiornate
    - Mantieni memoria del contesto della conversazione
    - Fornisci risposte accurate e dettagliate
    - Adatti il tuo stile comunicativo alle preferenze dell'utente

    Quando interagisci:
    1. Saluta sempre l'utente per nome se disponibile
    2. Usa gli strumenti quando necessario per fornire informazioni accurate
    3. Mantieni traccia delle interazioni per personalizzare l'esperienza
    4. Sii proattivo nel suggerire azioni utili

    Se l'utente chiede informazioni che richiedono dati aggiornati,
    usa sempre gli strumenti appropriati prima di rispondere.
    """

    # Crea l'istanza dell'Agent
    agent = Agent[AgentContext](
        name="IntelliBot",                   # Nome identificativo dell'agente
        instructions=instructions,           # Istruzioni comportamentali
        model="gpt-4o",                      # Modello LLM da utilizzare (più recente nel 2025)
        tools=[                              # Lista degli strumenti disponibili
            get_current_weather,
            search_web,
            calculate_math
        ],
        context=AgentContext(                # Contesto iniziale dell'agente
            session_id=f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ),
        max_turns=20,                        # Limite massimo di iterazioni per prevenire loop infiniti
        temperature=0.7,                     # Controllo della creatività delle risposte
    )

    return agent

def create_specialized_agent(specialty: str, tools_list: List = None) -> Agent:
    """
    Crea agenti specializzati per domini specifici.

    Args:
        specialty: Il dominio di specializzazione (es. "matematica", "meteo", "ricerca")
        tools_list: Lista personalizzata di strumenti per l'agente

    Returns:
        Agent specializzato configurato
    """

    # Definisce istruzioni specifiche basate sulla specializzazione
    specialty_instructions = {
        "matematica": "Sei un esperto matematico. Risolvi problemi numerici e fornisci spiegazioni dettagliate.",
        "meteo": "Sei un meteorologo esperto. Fornisci informazioni meteo accurate e consigli pratici.",
        "ricerca": "Sei un ricercatore esperto. Trova informazioni accurate e aggiornate su qualsiasi argomento."
    }

    # Strumenti predefiniti per ogni specializzazione
    specialty_tools = {
        "matematica": [calculate_math],
        "meteo": [get_current_weather],
        "ricerca": [search_web]
    }

    instructions = specialty_instructions.get(specialty, "Sei un assistente AI specializzato.")
    tools = tools_list or specialty_tools.get(specialty, [])

    agent = Agent(
        name=f"Agent_{specialty.title()}",   # Nome basato sulla specializzazione
        instructions=instructions,           # Istruzioni specifiche del dominio
        model="gpt-4o",
        tools=tools,                        # Strumenti pertinenti alla specializzazione
        temperature=0.3 if specialty == "matematica" else 0.7  # Meno creatività per matematica
    )

    return agent
```

## 2. Utilizzo di trace() per Tracciare il Comportamento

### Introduzione Teorica

Il sistema di tracing nell'OpenAI Agents SDK 2025 è fondamentale per debugging, monitoraggio e ottimizzazione degli agenti. Il tracing consente di:

- **Visualizzare il flusso di esecuzione**: Vedere ogni step dell'agente in dettaglio
- **Debugging**: Identificare errori e comportamenti imprevisti
- **Performance monitoring**: Misurare tempi di risposta e utilizzo risorse
- **Audit trail**: Mantenere un registro completo delle azioni
- **Integrazione con servizi esterni**: Esportare traces verso Logfire, AgentOps, Braintrust

Il sistema utilizza `with trace(...) as my_trace` come context manager per gestire automaticamente l'avvio e la chiusura delle tracce, garantendo un tracing pulito e strutturato.

### Implementazione Base del Tracing

```python
async def basic_tracing_example():
    """
    Esempio base di utilizzo del tracing per monitorare l'esecuzione dell'agente.
    """
    # Crea un'istanza dell'agente
    agent = create_intelligent_assistant()

    # Utilizza trace come context manager per tracciare l'intera operazione
    with trace(
        name="basic_agent_interaction",          # Nome identificativo della trace
        metadata={                               # Metadati aggiuntivi per la trace
            "agent_name": agent.name,
            "operation": "simple_query",
            "timestamp": datetime.datetime.now().isoformat(),
            "user_query_type": "weather_request"
        }
    ) as main_trace:

        # Aggiungi informazioni alla trace principale
        main_trace.log("Iniziando interazione con l'agente", level="info")
        main_trace.add_tag("environment", "development")
        main_trace.add_tag("agent_version", "v2025.09")

        try:
            # Query utente
            user_input = "Che tempo fa oggi a Milano?"

            # Registra l'input nella trace
            main_trace.log(f"Input utente ricevuto: {user_input}", level="info")

            # Esegui l'agente (Runner.run aggiunge automaticamente sub-traces)
            result = await Runner.run(agent, user_input)

            # Registra il risultato nella trace
            main_trace.log(f"Risposta generata: {result.final_output[:100]}...", level="info")
            main_trace.set_attribute("response_length", len(result.final_output))
            main_trace.set_attribute("tools_used", len(result.tool_calls) if hasattr(result, 'tool_calls') else 0)

            return result

        except Exception as e:
            # Registra gli errori nella trace
            main_trace.log(f"Errore durante l'esecuzione: {str(e)}", level="error")
            main_trace.set_status("error", str(e))
            raise

async def advanced_tracing_with_custom_spans():
    """
    Esempio avanzato che mostra l'utilizzo di span custom per tracciare
    operazioni specifiche all'interno del workflow dell'agente.
    """
    agent = create_intelligent_assistant()

    with trace(
        name="advanced_agent_workflow",
        metadata={"workflow_type": "multi_step_analysis"}
    ) as main_trace:

        # Span personalizzato per la fase di pre-processing
        with main_trace.span("preprocessing_phase") as prep_span:
            prep_span.log("Inizio preprocessing dell'input utente", level="debug")

            user_input = "Calcola 15 * 23 + 45, poi dimmi che tempo fa a Roma"

            # Simula analisi dell'input
            prep_span.set_attribute("input_length", len(user_input))
            prep_span.set_attribute("contains_math", "15 * 23" in user_input)
            prep_span.set_attribute("contains_weather_request", "tempo" in user_input)
            prep_span.log("Analisi input completata", level="debug")

        # Span per l'esecuzione dell'agente
        with main_trace.span("agent_execution") as exec_span:
            exec_span.log("Avvio esecuzione agente", level="info")

            start_time = datetime.datetime.now()
            result = await Runner.run(agent, user_input)
            end_time = datetime.datetime.now()

            # Calcola e registra metriche di performance
            execution_time = (end_time - start_time).total_seconds()
            exec_span.set_attribute("execution_time_seconds", execution_time)
            exec_span.set_attribute("final_output_length", len(result.final_output))

            exec_span.log(f"Esecuzione completata in {execution_time:.2f} secondi", level="info")

        # Span per post-processing
        with main_trace.span("postprocessing_phase") as post_span:
            post_span.log("Inizio post-processing della risposta", level="debug")

            # Simula validazione della risposta
            response_contains_math = any(char.isdigit() for char in result.final_output)
            response_contains_weather = "temp" in result.final_output.lower()

            post_span.set_attribute("response_contains_math_result", response_contains_math)
            post_span.set_attribute("response_contains_weather_info", response_contains_weather)
            post_span.log("Post-processing completato", level="debug")

        # Registra il risultato finale nella trace principale
        main_trace.set_attribute("workflow_success", True)
        main_trace.log("Workflow completato con successo", level="info")

        return result

def setup_external_tracing():
    """
    Configura l'integrazione del tracing con servizi esterni per
    monitoraggio avanzato e analytics.
    """
    # Configurazione per Logfire (esempio)
    from agents.tracing import configure_tracing

    # Configura destinazioni per le traces
    tracing_config = {
        "destinations": [
            {
                "type": "logfire",
                "token": "your_logfire_token",
                "project": "openai_agents_project"
            },
            {
                "type": "console",  # Output su console per development
                "level": "info"
            }
        ],
        "sampling_rate": 1.0,  # Traccia il 100% delle operazioni
        "enable_auto_instrumentation": True  # Traccia automaticamente le chiamate LLM
    }

    configure_tracing(tracing_config)
    print("Tracing configurato per servizi esterni")
```

## 3. Esecuzione dell'Agent tramite Runner.run

### Introduzione Teorica

Il Runner è il componente che gestisce l'esecuzione del workflow dell'agente, operando in un ciclo continuo fino alla generazione di un output finale. Il processo si articola nelle seguenti fasi:

1. **Invocazione Iniziale**: L'agente viene attivato con l'input dell'utente e le istruzioni di sistema, avviando il processo di elaborazione della richiesta
2. **Valutazione dell'Output**: Il Runner analizza la risposta dell'agente - se viene prodotto un output finale che soddisfa i criteri richiesti (tipo di dato, formato, completezza), il ciclo termina. In caso contrario, prosegue con le fasi successive
3. **Gestione degli Handoff**: Se l'agente determina che la richiesta necessita competenze specifiche di un altro agente, il Runner gestisce il passaggio di controllo, trasferendo contesto e stato al nuovo agente mantenendo la continuità della conversazione
4. **Esecuzione degli Strumenti**: Quando l'agente richiede l'utilizzo di tool esterni (API, funzioni, database), il Runner orchestra l'esecuzione delle chiamate, gestisce i risultati e li fornisce all'agente per continuare l'elaborazione

Il Runner può generare eccezioni in caso di superamento del limite di turni (MaxTurnsExceeded) o attivazione di guardrail di sicurezza.

### Esecuzione Base con Runner.run

```python
async def basic_runner_execution():
    """
    Esempio base di esecuzione di un agente tramite Runner.run.
    Mostra il pattern più semplice di utilizzo.
    """
    # Crea l'agente
    agent = create_intelligent_assistant()

    # Input utente semplice
    user_query = "Ciao! Puoi presentarti e dirmi che ore sono?"

    print(f"🤖 Eseguendo query: {user_query}")

    try:
        # Esecuzione sincrona dell'agente
        # Runner.run_sync è utile per script semplici
        result = await Runner.run(
            agent=agent,                    # L'agente da eseguire
            input=user_query,               # Input da processare
            context=AgentContext(           # Contesto personalizzato per questa esecuzione
                user_name="Marco",
                session_id="demo_session_001"
            )
        )

        # Il risultato contiene diversi attributi utili
        print(f"✅ Risposta finale: {result.final_output}")
        print(f"📊 Numero di turni: {result.turn_count}")
        print(f"🔧 Strumenti utilizzati: {len(result.tool_calls) if hasattr(result, 'tool_calls') else 0}")

        return result

    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {str(e)}")
        raise

async def advanced_runner_with_configuration():
    """
    Esempio avanzato che mostra le opzioni di configurazione
    disponibili per Runner.run.
    """
    agent = create_intelligent_assistant()

    # Input più complesso che richiederà multiple iterazioni
    complex_query = """
    Voglio pianificare una giornata a Milano domani.
    Puoi dirmi che tempo farà, calcolare quanto tempo serve
    per visitare 3 musei principali (assumendo 2 ore per museo + 30 min di spostamento),
    e suggerirmi il momento migliore della giornata?
    """

    print(f"🚀 Eseguendo query complessa...")

    # Configurazione avanzata del Runner
    runner_config = {
        "max_turns": 15,                    # Limite di turni per evitare loop infiniti
        "timeout": 60.0,                    # Timeout in secondi per l'intera esecuzione
        "enable_parallelization": True,     # Abilita esecuzione parallela dei tool calls
        "debug_mode": True                  # Abilita logging dettagliato
    }

    try:
        # Esecuzione con configurazione avanzata che include timeout, max_turns, parallelizzazione e debug
        result = await Runner.run(
            agent=agent,
            input=complex_query,
            context=AgentContext(
                user_name="Sofia",
                user_preferences={
                    "preferred_language": "italiano",
                    "timezone": "Europe/Rome",
                    "interests": ["arte", "cultura", "storia"]
                }
            ),
            **runner_config                 # Espande il dizionario runner_config come parametri nominali e non come un dizionario
                                            # Es. la prima chiave del dict runner_config "max_turns": 15 diventa max_turns=15
                                            # In pratica gli elementi del dict vengono estratti ed esposti come assegnazioni
        )

        # Analisi dettagliata del risultato
        print(f"✅ Esecuzione completata!")
        print(f"📝 Risposta finale:")
        print(f"   {result.final_output}")
        print(f"📊 Statistiche esecuzione:")
        print(f"   - Turni utilizzati: {result.turn_count}/{runner_config['max_turns']}")
        print(f"   - Tempo di esecuzione: {result.execution_time:.2f}s")

        # Se disponibili, mostra i dettagli dei tool calls
        if hasattr(result, 'tool_calls') and result.tool_calls:
            print(f"🔧 Strumenti utilizzati ({len(result.tool_calls)}):")
            # Itera su tutti i tool calls eseguiti dall'agente, numerandoli da 1
            # Per ogni chiamata mostra il nome della funzione chiamata e il suo stato di esecuzione
            # enumerate(result.tool_calls, 1) parte da 1 invece che 0 per una numerazione più user-friendly
            for i, tool_call in enumerate(result.tool_calls, 1):
                print(f"{i}. {tool_call.function_name}: {tool_call.status}")

        return result

    except Exception as e:
        print(f"❌ Errore durante l'esecuzione avanzata: {str(e)}")
        raise

async def multi_agent_runner_example():
    """
    Esempio di coordinazione di multiple agenti tramite Runner,
    mostrando il pattern di handoff tra agenti specializzati.
    """

    # Crea agenti specializzati
    math_agent = create_specialized_agent("matematica", [calculate_math])
    weather_agent = create_specialized_agent("meteo", [get_current_weather])
    research_agent = create_specialized_agent("ricerca", [search_web])

    # Agente coordinatore che decide quale agente utilizzare
    coordinator_instructions = """
    Sei un coordinatore di agenti specializzati.
    Analizza la richiesta dell'utente e determina quale agente specializzato dovrebbe gestirla:
    - Per calcoli matematici: usa Math_Agent
    - Per informazioni meteo: usa Weather_Agent
    - Per ricerche generali: usa Research_Agent

    Dopo aver ricevuto la risposta dall'agente specializzato,
    fornisci un riassunto finale all'utente.
    """

    coordinator = Agent(
        name="Coordinator_Agent",
        instructions=coordinator_instructions,
        model="gpt-4o",
        tools=[],  # Il coordinatore non ha strumenti diretti, coordina altri agenti
    )

    # Query che richiede coordinazione
    user_query = "Calcola l'area di un cerchio con raggio 5 metri e dimmi se oggi è una buona giornata per fare una passeggiata a Firenze"

    print(f"🎯 Coordinando multiple agenti per: {user_query}")

    with trace(name="multi_agent_coordination") as coord_trace:
        coord_trace.log("Avvio coordinazione multi-agente", level="info")

        try:
            # Fase 1: Il coordinatore analizza la richiesta
            with coord_trace.span("analysis_phase") as analysis_span:
                analysis_span.log("Analizzando richiesta utente", level="debug")

                # Il coordinatore determina che servono sia math_agent che weather_agent
                # In un'implementazione reale, questo potrebbe essere automatico

                analysis_span.set_attribute("agents_needed", ["math", "weather"])

            # Fase 2: Esecuzione agente matematico
            with coord_trace.span("math_agent_execution") as math_span:
                math_query = "Calcola l'area di un cerchio con raggio 5 metri"
                math_span.log(f"Eseguendo math_agent con: {math_query}", level="info")

                math_result = await Runner.run(math_agent, math_query)
                math_span.set_attribute("math_result", math_result.final_output)

            # Fase 3: Esecuzione agente meteo
            with coord_trace.span("weather_agent_execution") as weather_span:
                weather_query = "Che tempo fa a Firenze oggi? È una buona giornata per una passeggiata?"
                weather_span.log(f"Eseguendo weather_agent con: {weather_query}", level="info")

                weather_result = await Runner.run(weather_agent, weather_query)
                weather_span.set_attribute("weather_result", weather_result.final_output)

            # Fase 4: Il coordinatore combina i risultati
            with coord_trace.span("synthesis_phase") as synth_span:
                combined_context = f"""
                Risultato calcolo matematico: {math_result.final_output}
                Risultato informazioni meteo: {weather_result.final_output}

                Fornisci un riassunto finale combinando entrambe le informazioni per rispondere alla richiesta originale dell'utente.
                """

                synth_span.log("Sintetizzando risultati finali", level="info")

                final_result = await Runner.run(coordinator, combined_context)
                synth_span.set_attribute("final_synthesis", final_result.final_output)

            coord_trace.log("Coordinazione completata con successo", level="info")

            print(f"🎉 Risultato finale della coordinazione:")
            print(f"{final_result.final_output}")

            return {
                "math_result": math_result,
                "weather_result": weather_result,
                "final_result": final_result
            }

        except Exception as e:
            coord_trace.log(f"Errore nella coordinazione: {str(e)}", level="error")
            raise

# Funzione di esempio per testare tutti i componenti
async def comprehensive_example():
    """
    Esempio comprensivo che combina Agent creation, tracing e Runner execution
    in un workflow reale.
    """
    print("🚀 Avviando esempio comprensivo OpenAI Agents SDK 2025")

    # Setup tracing per l'intera sessione
    with trace(
        name="comprehensive_agent_demo",
        metadata={
            "demo_version": "2025.09",
            "components": ["Agent", "Trace", "Runner"]
        }
    ) as demo_trace:

        demo_trace.log("Inizio demo comprensiva", level="info")

        # 1. Creazione agenti
        with demo_trace.span("agent_creation") as creation_span:
            creation_span.log("Creando agenti specializzati", level="info")

            main_agent = create_intelligent_assistant()
            math_agent = create_specialized_agent("matematica")

            creation_span.set_attribute("agents_created", 2)

        # 2. Esecuzione scenario semplice
        with demo_trace.span("simple_scenario") as simple_span:
            simple_query = "Ciao! Calcola 42 * 13 e spiegami il risultato"
            simple_span.log(f"Eseguendo scenario semplice: {simple_query}", level="info")

            simple_result = await Runner.run(main_agent, simple_query)
            simple_span.set_attribute("simple_result_length", len(simple_result.final_output))

            print(f"📋 Risultato scenario semplice:")
            print(f"   {simple_result.final_output}")

        # 3. Esecuzione scenario complesso
        with demo_trace.span("complex_scenario") as complex_span:
            complex_query = "Che tempo fa a Venezia? E puoi calcolare quanti giorni mancano al 2026?"
            complex_span.log(f"Eseguendo scenario complesso: {complex_query}", level="info")

            complex_result = await Runner.run(main_agent, complex_query)
            complex_span.set_attribute("complex_result_length", len(complex_result.final_output))

            print(f"🧠 Risultato scenario complesso:")
            print(f"   {complex_result.final_output}")

        demo_trace.log("Demo comprensiva completata con successo", level="info")
        demo_trace.set_attribute("total_scenarios_executed", 2)

        return {
            "simple_result": simple_result,
            "complex_result": complex_result
        }

# Funzione principale per eseguire tutti gli esempi
async def main():
    """Funzione principale che esegue tutti gli esempi in sequenza."""

    print("=" * 60)
    print("🤖 OpenAI Agents SDK 2025 - Guida Completa")
    print("=" * 60)

    try:
        # Esempio 1: Esecuzione base
        print("\n1️⃣ Esecuzione Base del Runner")
        await basic_runner_execution()

        # Esempio 2: Tracing base
        print("\n2️⃣ Tracing Base")
        await basic_tracing_example()

        # Esempio 3: Esecuzione avanzata
        print("\n3️⃣ Esecuzione Avanzata con Configurazione")
        await advanced_runner_with_configuration()

        #
```
