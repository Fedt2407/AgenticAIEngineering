# Guida Pratica all'SDK OpenAI per Agentic AI

## Introduzione

Gli **Agenti AI** rappresentano l'evoluzione dei sistemi di intelligenza artificiale verso entità autonome capaci di:

- Ragionare su problemi complessi
- Utilizzare strumenti esterni (tools)
- Gestire conversazioni multi-turno
- Collaborare tra loro attraverso handoffs
- Operare in sicurezza attraverso guardrails

Questa guida ti accompagnerà attraverso tutti i concetti fondamentali con esempi pratici.

---

## 1. Setup e Configurazione Iniziale

### Installazione

```bash
# Installa l'SDK OpenAI
pip install openai

# Per funzionalità avanzate degli agenti
pip install openai[agents]

# Dipendenze aggiuntive per esempi completi
pip install python-dotenv requests pandas
```

### Configurazione Base

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Inizializza il client OpenAI
# La chiave API viene letta automaticamente da OPENAI_API_KEY
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # Specifica esplicitamente se necessario
)

# Verifica della connessione
try:
    # Test semplice per verificare che l'API funzioni
    response = client.models.list()
    print("✅ Connessione OpenAI stabilita con successo!")
except Exception as e:
    print(f"❌ Errore di connessione: {e}")
```

---

## 2. Fondamenti degli Agenti

### Anatomia di un Agente

Un agente OpenAI è composto da:

- **Istruzioni di sistema** (personalità e comportamento)
- **Modello** (GPT-4, GPT-4-turbo, ecc.)
- **Tools** (functions che l'agente può chiamare)
- **Risorse** (file, knowledge base)

### Creazione del Primo Agente

```python
from openai import OpenAI

client = OpenAI()

def create_basic_agent():
    """
    Crea un agente semplice con personalità definita
    """

    # Crea l'agente specificando le sue caratteristiche
    agent = client.beta.agents.create(
        # Nome identificativo dell'agente
        name="Assistente Matematico",

        # Istruzioni che definiscono personalità e comportamento
        instructions="""
        Sei un esperto matematico specializzato in algebra e calcolo.

        Comportamenti chiave:
        - Spiega sempre i passaggi step-by-step
        - Usa esempi concreti quando possibile
        - Se non sei sicuro, ammettilo onestamente
        - Mantieni un tono paziente e incoraggiante
        """,

        # Modello da utilizzare (GPT-4 consigliato per agenti)
        model="gpt-4-turbo-preview",

        # Strumenti disponibili (inizialmente nessuno)
        tools=[],

        # Metadati opzionali per organizzazione
        # I metadati sono informazioni aggiuntive che possiamo associare all'agente
        # Servono per:
        # - Organizzare e categorizzare gli agenti
        # - Tracciare versioni e modifiche nel tempo
        # - Filtrare e cercare agenti specifici
        # - Aggiungere informazioni personalizzate utili per il nostro use case
        metadata={
            "categoria": "educazione",
            "versione": "1.0",
            "creato_da": "tutorial"
        }
    )

    print(f"✅ Agente creato con ID: {agent.id}")
    return agent

# Esempio di utilizzo
math_agent = create_basic_agent()
```

### Interazione con l'Agente

```python
def chat_with_agent(agent_id, user_message):
    """
    Gestisce una conversazione con l'agente
    """

    # Crea una nuova sessione di conversazione (thread)
    thread = client.beta.threads.create(
        # Metadati opzionali per tracciare la conversazione
        metadata={
            "user_id": "user_123",
            "topic": "matematica"
        }
    )

    # Aggiunge il messaggio dell'utente al thread
    # Usiamo threads.messages.create() invece di chat.completions.create() perché:
    # 1. Stiamo lavorando con un agente che mantiene una conversazione persistente (thread)
    # 2. threads.messages permette di aggiungere messaggi a una conversazione esistente
    # 3. chat.completions è per singole chiamate stateless, mentre threads mantiene il contesto
    # 4. Gli agenti OpenAI usano threads per gestire conversazioni lunghe e complesse
    message = client.beta.threads.messages.create(
        thread_id=thread.id,        # ID del thread per mantenere il contesto; non viene usato con chat.completions.create() in quanto stateless senza contesto
        role="user",                # Chi sta parlando (utente vs assistente)
        content=user_message        # Il contenuto effettivo del messaggio che viene passato come parametro alla funzione
    )

    # Esegue l'agente sul thread per generare una risposta
    # Il metodo .runs crea una nuova esecuzione dell'agente sul thread
    # Questo è come "premere invio" in una chat - l'agente processa tutti i messaggi
    # nel thread e genera una risposta. L'esecuzione è asincrona e può richiedere
    # del tempo, per questo dopo viene controllato lo status del run in un loop
    run = client.beta.threads.runs.create(
        thread_id=thread.id,        # Su quale conversazione lavorare
        assistant_id=agent_id,      # Quale agente utilizzare

        # Istruzioni aggiuntive per questo specifico run
        additional_instructions="Rispondi in italiano e sii molto dettagliato."
    )

    # Attende che l'agente completi l'elaborazione
    while run.status in ["queued", "in_progress"]:
        # Controlla lo stato ogni secondo
        time.sleep(1)
        # Recupera lo stato aggiornato del run usando l'ID del thread e del run
        # .retrieve() fa una chiamata API per ottenere le informazioni più recenti sull'esecuzione
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    if run.status == "completed":
        # Recupera tutti i messaggi nel thread
        # .messages è il namespace per gestire i messaggi in un thread
        # .list() recupera tutti i messaggi nel thread come una lista paginata
        # - thread_id: identifica il thread da cui recuperare i messaggi
        # - order="asc": ordina i messaggi dal più vecchio (ascending)
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc"  # Dal più vecchio al più nuovo
        )

        # Trova l'ultima risposta dell'agente
        # reversed() inverte l'ordine dei messaggi per trovare l'ultimo messaggio dell'assistente partendo dal più recente
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                # Estrae il contenuto testuale
                # msg.content[0].text.value è usato invece di msg.choices[0].message.content perché:
                # - Stiamo usando l'API Assistants (threads) e non l'API Chat Completions
                # - Nelle API Assistants, le risposte sono strutturate come una lista di contenuti (msg.content)
                # - Ogni contenuto può essere di tipo diverso (testo, immagini, etc)
                # - [0] prende il primo contenuto della lista
                # - .text.value estrae il valore testuale da quel contenuto
                return msg.content[0].text.value
    else:
        return f"Errore nell'esecuzione: {run.status}"

# Esempio di utilizzo
# La funzione chat_with_agent() gestisce una conversazione con un assistente OpenAI:
# - Crea un thread per la conversazione
# - Aggiunge il messaggio dell'utente
# - Avvia un'esecuzione dell'assistente specificato (math_agent.id)
# - Attende il completamento monitorando lo stato
# - Recupera e restituisce l'ultima risposta dell'assistente
risposta = chat_with_agent(
    math_agent.id,  # ID dell'assistente matematico da utilizzare
    "Come risolvo l'equazione 2x + 5 = 13?"  # Messaggio da processare
)
print(risposta)
```

---

## 3. Tools (Strumenti) per gli Agenti

### Tipi di Tools Disponibili

1. **Function Calling**: Permette di definire e utilizzare funzioni Python personalizzate che l'agente può chiamare per eseguire operazioni specifiche come calcoli, chiamate API o accesso a database
2. **Code Interpreter**: Ambiente di esecuzione sicuro che consente all'agente di scrivere ed eseguire codice Python per analisi dati, visualizzazioni e calcoli complessi
3. **File Search**: Capacità di cercare, leggere e analizzare contenuti all'interno di documenti caricati come PDF, fogli di calcolo e file di testo
4. **Built-in Tools**: Set di strumenti predefiniti forniti da OpenAI che includono funzionalità comuni come la manipolazione di date, la formattazione del testo e operazioni matematiche

### Implementazione di Function Tools

```python
import json
import requests

# Questa funzione creerà un agente con le funzionalità più recenti dell'SDK di OpenAI es. deepseek.beta.assistance.create()
# Viene creato anche il JSON per passare i tool all'agente (in questo esempio non usiamo il decoratore @function_tool)
def create_agent_with_tools():
    """
    Crea un agente con strumenti personalizzati
    """

    # Definizione degli strumenti disponibili
    tools = [
        {
            "type": "function",
            "function": {
                # Nome della funzione (deve corrispondere alla funzione Python)
                "name": "get_weather",

                # Descrizione per l'agente (importante per la scelta)
                "description": "Ottiene le condizioni meteorologiche per una città specifica",

                # Schema JSON dei parametri
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Nome della città per cui ottenere il meteo"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Unità di misura della temperatura"
                        }
                    },
                    "required": ["city"]  # Parametri obbligatori
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_mortgage",
                "description": "Calcola la rata mensile di un mutuo",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "principal": {
                            "type": "number",
                            "description": "Importo del prestito in euro"
                        },
                        "rate": {
                            "type": "number",
                            "description": "Tasso di interesse annuale (es: 3.5 per 3.5%)"
                        },
                        "years": {
                            "type": "integer",
                            "description": "Durata del mutuo in anni"
                        }
                    },
                    "required": ["principal", "rate", "years"]
                }
            }
        },
        # Abilita il code interpreter che permette all'assistente di:
        # - Eseguire codice Python per calcoli matematici complessi
        # - Analizzare e manipolare dati strutturati
        # - Generare visualizzazioni e grafici
        # - Lavorare con librerie scientifiche come numpy e pandas
        {
            "type": "code_interpreter"
        }
    ]

    # Crea l'agente con gli strumenti
    # Usiamo client.beta.assistants.create invece di Runner.run perché:
    # 1. Gli Assistants API sono una feature più recente e moderna di OpenAI
    # 2. Offrono funzionalità native per la gestione degli strumenti e del contesto
    # 3. Mantengono lo stato della conversazione lato server
    # 4. Supportano nativamente Code Interpreter e retrieval
    # 5. Sono ottimizzati per conversazioni lunghe e complesse
    agent = client.beta.assistants.create(
        name="Assistente Multifunzione",
        instructions="""
        Sei un assistente pratico che può:
        1. Fornire informazioni meteorologiche
        2. Calcolare rate di mutui
        3. Eseguire calcoli matematici complessi

        Usa sempre gli strumenti disponibili quando appropriato.
        Spiega i calcoli e fornisci contesto utile.
        """,
        model="gpt-4-turbo-preview",
        tools=tools
    )

    return agent

# Implementazione delle funzione chiamabili dal tool (il nome deve essere lo stesso della chiave "name" del JSON)
def get_weather(city, units="celsius"):
    """
    Simula una chiamata API meteorologica
    In produzione, useresti una vera API come OpenWeatherMap
    """
    # Simulazione dati meteo
    weather_data = {
        "Roma": {"temp": 22, "condition": "Soleggiato"},
        "Milano": {"temp": 18, "condition": "Nuvoloso"},
        "Venezia": {"temp": 25, "condition": "Parzialmente nuvoloso"}
    }

    if city in weather_data:
        data = weather_data[city]
        temp = data["temp"]

        # Converte in Fahrenheit se richiesto
        if units == "fahrenheit":
            temp = temp * 9/5 + 32

        return {
            "city": city,
            "temperature": temp,
            "condition": data["condition"],
            "units": units
        }
    else:
        return {"error": f"Dati meteo non disponibili per {city}"}

# Implementazione delle funzione chiamabili dal tool (il nome deve essere lo stesso della chiave "name" del JSON)
def calculate_mortgage(principal, rate, years):
    """
    Calcola la rata mensile di un mutuo usando la formula standard
    """
    # Converte il tasso annuale in tasso mensile decimale
    monthly_rate = (rate / 100) / 12

    # Numero totale di pagamenti
    num_payments = years * 12

    if monthly_rate == 0:
        # Se il tasso è 0%, la rata è semplicemente l'importo diviso per i mesi
        monthly_payment = principal / num_payments
    else:
        # Formula del mutuo: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        monthly_payment = principal * (
            monthly_rate * (1 + monthly_rate)**num_payments
        ) / (
            (1 + monthly_rate)**num_payments - 1
        )

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_paid": round(monthly_payment * num_payments, 2),
        "total_interest": round(monthly_payment * num_payments - principal, 2)
    }
```

### Gestione delle Function Calls

```python
def handle_agent_with_tools(agent_id, user_message):
    """
    Gestisce conversazioni con agenti che usano strumenti
    """

    # Crea thread e messaggio come prima. NOTA: si usa .beta.threads.create() per gestire l'intero contesto della conversazione
    # al posto di .completions.create() che è stateless e non è in grado di gestire il contesto della conversazione
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # Esegue l'agente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=agent_id
    )

    # Loop di gestione run con tool calls
    while True:
        # Controlla lo stato del run
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run.status == "completed":
            # Run completato con successo
            break

        elif run.status == "requires_action":
            # L'agente vuole chiamare una funzione

            # Estrae le tool calls richieste
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            # Elabora ogni tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name

                # Parse degli argomenti JSON
                arguments = json.loads(tool_call.function.arguments)

                print(f"🔧 Chiamata funzione: {function_name}")
                print(f"📋 Argomenti: {arguments}")

                # Router per le funzioni disponibili
                if function_name == "get_weather":
                    result = get_weather(**arguments)
                elif function_name == "calculate_mortgage":
                    result = calculate_mortgage(**arguments)
                else:
                    result = {"error": f"Funzione {function_name} non trovata"}

                # Prepara l'output per l'agente
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result, ensure_ascii=False)
                })

            # Invia i risultati delle funzioni all'agente per continuare l'esecuzione
            # Dopo che le funzioni richieste sono state eseguite, i loro output vengono
            # inviati all'agente tramite submit_tool_outputs per permettergli di
            # elaborare una risposta finale incorporando i risultati ottenuti
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        elif run.status in ["failed", "cancelled", "expired"]:
            # Gestione errori
            print(f"❌ Run fallito con stato: {run.status}")
            break

        else:
            # Stati in attesa (queued, in_progress)
            time.sleep(1)

    # Recupera la risposta finale
    # NOTA: Usiamo threads.messages.list() invece di response.choices[0].message.content perché:
    # 1. Stiamo usando l'API Assistants che gestisce conversazioni attraverso thread
    # 2. I messaggi sono memorizzati nel thread e vanno recuperati esplicitamente
    # 3. Questo metodo ci dà accesso a tutto lo storico della conversazione
    # 4. È più robusto perché gestisce anche messaggi multipli e file allegati
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc"
    )

    # Trova l'ultima risposta dell'assistente
    for message in reversed(messages.data):
        if message.role == "assistant":
            return message.content[0].text.value

    return "Nessuna risposta ricevuta"

# Esempio di utilizzo
agent_with_tools = create_agent_with_tools()

# Test con richiesta meteo
response = handle_agent_with_tools(
    agent_with_tools.id,
    "Che tempo fa a Roma? E puoi anche calcolarmi la rata di un mutuo da 200000 euro al 3.5% per 25 anni?"
)

print(response)
```

---

## 4. Session Management

### Gestione delle Sessioni Persistenti

```python

# Le sessioni persistenti sono un meccanismo fondamentale per mantenere il contesto
# e lo stato di una conversazione tra un utente e un agente AI nel tempo.
#
# Benefici principali:
# - Mantengono la memoria della conversazione permettendo riferimenti a messaggi precedenti
# - Consentono di tracciare lo stato e le preferenze dell'utente
# - Permettono di riprendere conversazioni interrotte
# - Facilitano l'analisi e il debug delle interazioni
#
# In OpenAI, le sessioni sono implementate attraverso i "Thread":
# - Ogni thread rappresenta una conversazione distinta
# - I messaggi vengono aggiunti sequenzialmente al thread
# - Il contesto viene mantenuto automaticamente
# - I thread persistono anche dopo la chiusura della connessione
#
# La classe AgentSession fornisce un'interfaccia di alto livello per:
# - Gestire thread e messaggi
# - Tracciare statistiche e metriche
# - Implementare logica custom (es. timeout, limiti, etc)
# - Gestire errori e stati anomali
class AgentSession:
    """
    Classe per gestire sessioni persistenti con gli agenti
    """

    def __init__(self, agent_id, user_id=None):
        # ID dell'agente da utilizzare
        self.agent_id = agent_id

        # ID utente per tracking (opzionale)
        self.user_id = user_id

        # Thread della conversazione (inizialmente None)
        self.thread_id = None

        # Storico messaggi per debug/logging
        self.message_history = []

        # Stato della sessione
        self.session_data = {
            "created_at": None,
            "last_activity": None,
            "message_count": 0
        }

    def start_session(self, initial_context=None):
        """
        Inizia una nuova sessione di conversazione
        """
        import datetime

        # I thread metadata sono dati aggiuntivi associati al thread che aiutano a:
        # - Tracciare informazioni sulla sessione (es. quando è iniziata)
        # - Identificare l'utente che ha avviato la conversazione
        # - Aggiungere dati di contesto utili per l'elaborazione
        # - Facilitare il recupero e la gestione dei thread
        thread_metadata = {
            "user_id": self.user_id,  # ID dell'utente per identificare chi ha creato il thread
            "session_start": datetime.datetime.now().isoformat()  # Timestamp di inizio sessione
        }

        # Aggiunge contesto iniziale ai metadati se fornito
        if initial_context:
            thread_metadata.update(initial_context)

        thread = client.beta.threads.create(
            metadata=thread_metadata
        )

        # Salva l'ID del thread
        self.thread_id = thread.id

        # Aggiorna i dati della sessione
        now = datetime.datetime.now()
        self.session_data.update({
            "created_at": now,
            "last_activity": now,
            "message_count": 0
        })

        print(f"✅ Sessione avviata - Thread ID: {self.thread_id}")
        return self.thread_id

    def send_message(self, content, role="user"):
        """
        Invia un messaggio nella sessione corrente
        """
        if not self.thread_id:
            raise ValueError("Sessione non avviata. Chiamare start_session() prima.")

        import datetime

        # Crea il messaggio nel thread
        message = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role=role,
            content=content
        )

        # Aggiunge al tracking locale
        self.message_history.append({
            "timestamp": datetime.datetime.now(),
            "role": role,
            "content": content,
            "message_id": message.id
        })

        # Aggiorna statistiche sessione
        self.session_data["last_activity"] = datetime.datetime.now()
        self.session_data["message_count"] += 1

        return message.id

    def get_agent_response(self, additional_instructions=None):
        """
        Ottiene una risposta dall'agente
        """
        if not self.thread_id:
            raise ValueError("Sessione non avviata.")

        # Configura parametri del run
        run_params = {
            "thread_id": self.thread_id,
            "assistant_id": self.agent_id
        }

        # Aggiunge istruzioni aggiuntive se specificate
        if additional_instructions:
            run_params["additional_instructions"] = additional_instructions

        # Avvia l'esecuzione
        run = client.beta.threads.runs.create(**run_params)

        # Gestisce il run (incluse eventuali tool calls)
        response = self._handle_run(run)

        # Traccia la risposta
        if response:
            self.message_history.append({
                "timestamp": datetime.datetime.now(),
                "role": "assistant",
                "content": response,
                "message_id": None
            })

        return response

    def _handle_run(self, run):
        """
        Gestisce l'esecuzione di un run con supporto per tool calls
        """
        while True:
            # Aggiorna lo stato del run
            run = client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )

            if run.status == "completed":
                # Run completato - recupera la risposta
                messages = client.beta.threads.messages.list(
                    thread_id=self.thread_id,
                    order="desc",
                    limit=1  # Limita il risultato all'ultimo messaggio della conversazione
                )

                if messages.data and messages.data[0].role == "assistant":
                    return messages.data[0].content[0].text.value
                return None

            elif run.status == "requires_action":
                # Gestisce tool calls (implementazione semplificata)
                self._handle_tool_calls(run)

            elif run.status in ["failed", "cancelled", "expired"]:
                print(f"❌ Run fallito: {run.status}")
                return None

            else:
                # In attesa - pausa breve
                time.sleep(0.5)

    def _handle_tool_calls(self, run):
        """
        Gestisce le chiamate agli strumenti (versione semplificata)
        """
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            # In questa versione dimostrativa, implementiamo solo alcuni strumenti essenziali
            # In un ambiente di produzione, dovresti implementare un router più sofisticato che:
            # - Gestisce tutti gli strumenti disponibili in modo modulare
            # - Include gestione degli errori e logging
            # - Implementa controlli di sicurezza e validazione input
            # - Supporta il caricamento dinamico di nuovi strumenti
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Router base che gestisce solo lo strumento get_weather
            # In produzione questo sarebbe sostituito da un sistema di routing più robusto
            # basato su decoratori che permettono di registrare automaticamente le funzioni
            # come strumenti disponibili. Ad esempio:
            # @tool_registry
            # def get_weather(location: str) -> dict:
            #     ...
            # Il decoratore si occuperebbe di:
            # - Registrare la funzione nel registro degli strumenti
            # - Validare i parametri di input/output
            # - Gestire logging e monitoraggio
            # - Applicare policy di sicurezza e rate limiting
            if function_name == "get_weather":
                result = get_weather(**arguments)
            else:
                result = {"error": f"Tool {function_name} non supportato in questa sessione"}

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result, ensure_ascii=False)
            })

        # Invia i risultati
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    def get_conversation_history(self, limit=50):
        """
        Recupera lo storico della conversazione
        """
        if not self.thread_id:
            return []

        messages = client.beta.threads.messages.list(
            thread_id=self.thread_id,
            order="asc",
            limit=limit # è un parametro passato alla funzione. Di defaul = 50.
        )

        history = []
        for message in messages.data:
            history.append({
                "role": message.role,
                "content": message.content[0].text.value,
                "timestamp": message.created_at
            })

        return history

    def get_session_stats(self):
        """
        Restituisce statistiche della sessione
        """
        # L'operatore ** è necessario per unire i due dizionari:
        # - il dizionario con i dati base della sessione (thread_id, user_id, agent_id, total_messages)
        # - il dizionario self.session_data che contiene i dati custom della sessione
        return {
            "thread_id": self.thread_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            **self.session_data,
            "total_messages": len(self.message_history)
        }

    def close_session(self):
        """
        Chiude la sessione (opzionale - per cleanup)
        """
        # In OpenAI, i thread persistono automaticamente
        # Questa funzione è per cleanup locale
        self.thread_id = None
        print("✅ Sessione chiusa localmente")


# Esempio di utilizzo della gestione sessioni
def demo_session_management():
    """
    Dimostra l'uso delle sessioni persistenti con un esempio pratico di conversazione
    che mostra come l'agente mantiene il contesto tra più interazioni.
    """

    # Crea un agente semplice per il test usando l'API OpenAI Assistants
    # Specifichiamo nome, istruzioni di base e modello da utilizzare
    agent = client.beta.assistants.create(
        name="Assistente Sessioni",
        instructions="Sei un assistente che ricorda il contesto delle conversazioni.",
        model="gpt-4-turbo-preview"
    )

    # Inizializza una nuova sessione di conversazione
    # Richiede l'ID dell'agente creato e un ID utente univoco
    session = AgentSession(
        agent_id=agent.id,
        user_id="user_demo_123"
    )

    # Avvia la sessione con dati custom che personalizzano il contesto:
    # - topic: definisce l'argomento principale della conversazione (programmazione)
    # - difficulty_level: permette all'agente di adattare le risposte al livello dell'utente
    session.start_session({
        "topic": "programmazione",
        "difficulty_level": "intermedio"
    })

    # Inizia una conversazione multi-turno per dimostrare il mantenimento del contesto
    # Prima interazione: l'utente si presenta
    print("=== Conversazione 1 ===")
    session.send_message("Ciao! Mi chiamo Federico e sto imparando Python.")
    response1 = session.get_agent_response()
    print(f"Agente: {response1}")

    # Seconda interazione: domanda tecnica sulla programmazione Python
    print("\n=== Conversazione 2 ===")
    session.send_message("Puoi spiegarmi cosa sono le list comprehensions?")
    response2 = session.get_agent_response()
    print(f"Agente: {response2}")

    # Terza interazione: verifica che l'agente ricordi informazioni precedenti
    # In questo caso, il nome dell'utente menzionato nella prima interazione
    print("\n=== Conversazione 3 ===")
    session.send_message("Ricordi il mio nome?")
    response3 = session.get_agent_response()
    print(f"Agente: {response3}")

    # Visualizza le statistiche della sessione, inclusi i dati custom
    # e le informazioni di base come thread_id e numero totale di messaggi
    print(f"\n=== Statistiche Sessione ===")
    stats = session.get_session_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Chiude la sessione e pulisce le risorse locali
    # I dati della conversazione rimangono comunque persistenti su OpenAI
    session.close_session()

# Esegui la demo
# demo_session_management()
```

---

## 5. Handoffs tra Agenti

### Concetto di Handoff

Gli **handoffs** permettono di trasferire una conversazione da un agente all'altro, mantenendo il contesto. Utile per:

- Specializzazioni diverse (vendite → supporto tecnico)
- Escalation (livello 1 → livello 2)
- Workflow complessi

### Implementazione Sistema Handoff

```python
class AgentHandoffManager:
    """
    Gestisce il trasferimento di conversazioni tra agenti
    """

    def __init__(self):
        # Registry degli agenti disponibili
        self.agents = {}

        # Regole di handoff
        self.handoff_rules = {}

        # Storico dei trasferimenti
        self.handoff_history = []

    def register_agent(self, agent_id, agent_type, capabilities=None, handoff_triggers=None):
        """
        Registra un nuovo agente nel sistema di handoff.

        Args:
            agent_id (str): Identificatore univoco dell'agente
            agent_type (str): Tipo/ruolo dell'agente (es. "sales", "support", "specialist")
            capabilities (list, optional): Lista delle capacità/competenze dell'agente. Default None.
            handoff_triggers (list, optional): Lista di trigger che attivano il trasferimento da questo agente. Default None.

        L'agente viene registrato nel dizionario self.agents usando agent_type come chiave.
        Per ogni agente vengono memorizzati:
        - id: identificatore univoco
        - capabilities: lista delle competenze/capacità
        - handoff_triggers: condizioni che attivano il trasferimento ad altri agenti

        Se capabilities o handoff_triggers non sono specificati, vengono inizializzati come liste vuote.
        """
        self.agents[agent_type] = {
            "id": agent_id,
            "capabilities": capabilities or [],
            "handoff_triggers": handoff_triggers or []
        }

        print(f"✅ Agente '{agent_type}' registrato (ID: {agent_id})")

    def add_handoff_rule(self, from_agent, to_agent, trigger_keywords, condition_func=None):
        """
        Aggiunge una regola di handoff automatico tra due agenti.

        Args:
            from_agent (str): L'agente di origine che inizia il trasferimento
            to_agent (str): L'agente di destinazione che riceve il trasferimento
            trigger_keywords (list): Lista di parole chiave che attivano il trasferimento quando presenti nel messaggio utente
            condition_func (callable, optional): Funzione opzionale che implementa logica aggiuntiva per il trasferimento.
            Riceve il messaggio utente e il contesto della conversazione come parametri. Default None.

        La regola viene salvata nel dizionario self.handoff_rules usando un ID univoco generato dai nomi degli agenti.
        Quando la regola è attiva, il sistema controlla:
        1. Se il messaggio utente contiene una delle parole chiave specificate
        2. Se la condition_func (se presente) restituisce True

        Se entrambe le condizioni sono soddisfatte, viene eseguito il trasferimento all'agente di destinazione.
        """
        rule_id = f"{from_agent}_to_{to_agent}"

        self.handoff_rules[rule_id] = {
            "from": from_agent,
            "to": to_agent,
            "keywords": trigger_keywords,
            "condition": condition_func
        }

        print(f"✅ Regola handoff aggiunta: {from_agent} → {to_agent}")

    def should_handoff(self, current_agent_type, user_message, conversation_context=None):
        """
        Determina se è necessario trasferire la conversazione ad un altro agente in base alle regole di handoff definite nel metodo add_handoff_rule

        Args:
            current_agent_type (str): Il tipo dell'agente attualmente attivo
            user_message (str): Il messaggio dell'utente da analizzare
            conversation_context (dict, optional): Contesto aggiuntivo della conversazione. Default None.

        Returns:
            str or None: Il tipo dell'agente a cui trasferire la conversazione se viene trovata una regola di handoff valida, None altrimenti.

        Note:
            La funzione controlla tutte le regole di handoff definite per l'agente corrente e verifica:
            1. Se il messaggio utente contiene una delle parole chiave trigger
            2. Se la condition_func associata (se presente) restituisce True

            Il trasferimento viene attivato solo se entrambe le condizioni sono soddisfatte.
        """
        for rule_id, rule in self.handoff_rules.items():
            if rule["from"] == current_agent_type:

                # Controlla keyword triggers
                message_lower = user_message.lower()
                keyword_match = any(
                    keyword in message_lower
                    for keyword in rule["keywords"]
                )

                if keyword_match:
                    # Se c'è una condizione aggiuntiva, la verifica
                    if rule["condition"]:
                        if rule["condition"](user_message, conversation_context):
                            return rule["to"]
                    else:
                        return rule["to"]

        return None

    def execute_handoff(self, thread_id, from_agent_type, to_agent_type, handoff_reason=""):
        """
        Esegue il trasferimento effettivo della conversazione da un agente ad un altro.

        Args:
            thread_id (str): L'ID del thread della conversazione da trasferire
            from_agent_type (str): Il tipo dell'agente che sta cedendo la conversazione
            to_agent_type (str): Il tipo dell'agente che sta ricevendo la conversazione
            handoff_reason (str, optional): Il motivo del trasferimento. Default "".

        Returns:
            str: L'ID dell'agente a cui è stata trasferita la conversazione

        Raises:
            ValueError: Se uno degli agenti specificati non esiste nel sistema

        Note:
            La funzione:
            1. Verifica l'esistenza di entrambi gli agenti
            2. Aggiunge un messaggio di transizione al thread per informare l'utente
            3. Registra i metadati del trasferimento
            4. Aggiunge il trasferimento allo storico
            5. Restituisce l'ID del nuovo agente
        """
        import datetime

        # Verifica che entrambi gli agenti esistano
        if from_agent_type not in self.agents or to_agent_type not in self.agents:
            raise ValueError(f"Agente non trovato: {from_agent_type} o {to_agent_type}")

        from_agent = self.agents[from_agent_type]
        to_agent = self.agents[to_agent_type]

        # Aggiunge messaggio di transizione al thread
        handoff_message = f"""
        🔄 TRASFERIMENTO CONVERSAZIONE
        Ciao! Sono {to_agent_type} e continuerò ad assisterti da qui.
        Motivo del trasferimento: {handoff_reason}
        Come posso aiutarti?
        """

        # Invia il messaggio di transizione
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=handoff_message,
            metadata={
                "handoff": True,
                "from_agent": from_agent_type,
                "to_agent": to_agent_type,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

        # Registra l'handoff
        handoff_record = {
            "timestamp": datetime.datetime.now(),
            "thread_id": thread_id,
            "from_agent": from_agent_type,
            "to_agent": to_agent_type,
            "reason": handoff_reason
        }

        self.handoff_history.append(handoff_record)

        print(f"🔄 Handoff eseguito: {from_agent_type} → {to_agent_type}")

        return to_agent["id"]

class ConversationWithHandoffs:
    """
    Gestisce conversazioni multi-agente con supporto per il trasferimento automatico tra agenti specializzati.

    Questa classe implementa un sistema di gestione delle conversazioni che può:
    - Avviare conversazioni con un agente iniziale
    - Valutare automaticamente quando è necessario un trasferimento ad altro agente
    - Eseguire trasferimenti fluidi mantenendo il contesto della conversazione
    - Tracciare lo stato della conversazione inclusi topic, sentiment e livello di complessità

    Attributes:
        handoff_manager: Gestore dei trasferimenti tra agenti
        current_agent_type: Tipo dell'agente attualmente attivo
        current_agent_id: ID dell'agente attualmente attivo
        thread_id: ID del thread di conversazione corrente
        conversation_context: Dizionario contenente metadati sulla conversazione come:
            - topic: Argomento principale della conversazione
            - user_sentiment: Sentiment dell'utente (neutral, positive, negative)
            - complexity_level: Livello di complessità della conversazione (basic, advanced)
    """

    def __init__(self, handoff_manager):
        self.handoff_manager = handoff_manager # è la classe per la gestione degli handoff AgentHandoffManager definita più sopra
        self.current_agent_type = None
        self.current_agent_id = None
        self.thread_id = None
        self.conversation_context = {
            "topic": None,
            "user_sentiment": "neutral",
            "complexity_level": "basic"
        }

    def start_conversation(self, initial_agent_type, user_message):
        """
        Inizia una nuova conversazione con un agente specifico.

        Args:
            initial_agent_type (str): Il tipo di agente con cui iniziare la conversazione.
            Deve essere un tipo di agente già registrato nel handoff_manager.
            user_message (str): Il primo messaggio dell'utente che avvia la conversazione.

        Returns:
            dict: La risposta dell'agente al primo messaggio dell'utente.

        Raises:
            ValueError: Se il tipo di agente specificato non è registrato nel sistema.

        Note:
            Questo metodo:
            1. Verifica la validità dell'agente richiesto
            2. Configura l'agente iniziale
            3. Crea un nuovo thread di conversazione
            4. Invia il primo messaggio dell'utente
        """
        # Verifica che l'agente esista
        if initial_agent_type not in self.handoff_manager.agents:
            raise ValueError(f"Agente {initial_agent_type} non registrato")

        # Imposta l'agente corrente
        self.current_agent_type = initial_agent_type
        self.current_agent_id = self.handoff_manager.agents[initial_agent_type]["id"]

        # Crea il thread
        thread = client.beta.threads.create()
        self.thread_id = thread.id

        # Invia il primo messaggio
        return self.send_message(user_message)

    def send_message(self, user_message):
        """
        Invia un messaggio all'agente corrente e gestisce eventuali handoff ad altri agenti.

        Args:
            user_message (str): Il messaggio dell'utente da inviare all'agente

        Returns:
            str: La risposta dell'agente al messaggio dell'utente

        Note:
            Il metodo:
            1. Verifica se è necessario un handoff ad un altro agente
            2. Se necessario, esegue l'handoff al nuovo agente
            3. Aggiunge il messaggio dell'utente al thread
            4. Ottiene e restituisce la risposta dall'agente corrente

        Raises:
            ClientError: Se si verifica un errore nella comunicazione con l'API
            HandoffError: Se si verifica un errore durante l'handoff tra agenti
        """
        # Controlla se è necessario un handoff utilizzando il metodo precedentemente definito
        target_agent_type = self.handoff_manager.should_handoff(
            self.current_agent_type,
            user_message,
            self.conversation_context
        )

        # Se necessario, esegue l'handoff anche in questo caso usando il metodo definito all'interno della classe AgentHandoffManager
        if target_agent_type and target_agent_type != self.current_agent_type:
            self.current_agent_id = self.handoff_manager.execute_handoff(
                self.thread_id,
                self.current_agent_type,
                target_agent_type,
                f"Richiesta dell'utente richiede competenze di {target_agent_type}"
            )
            self.current_agent_type = target_agent_type

        # Aggiunge il messaggio al thread
        client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=user_message
        )

        # Ottiene risposta dall'agente corrente
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.current_agent_id
        )

        # Gestisce l'esecuzione usando il metodo privato _wait_for_response che viene definito di seguito
        return self._wait_for_response(run)

    def _wait_for_response(self, run):
        """
        Attende e recupera la risposta dell'agente OpenAI.

        Args:
            run: L'oggetto Run restituito dalla creazione di una nuova esecuzione

        Returns:
            str: Il contenuto testuale della risposta dell'agente se completata con successo
            None: Se non ci sono messaggi disponibili
            str: Un messaggio di errore se l'esecuzione fallisce

        Note:
            Il metodo controlla periodicamente lo stato dell'esecuzione finché non è completata
            o fallita. Quando completata, recupera l'ultimo messaggio dal thread.
            Include gestione degli stati di errore come failed, cancelled ed expired.
        """
        while True:
            # Recupera lo stato corrente dell'esecuzione utilizzando l'ID del thread e l'ID della run
            # Questo metodo fa una chiamata API a OpenAI per ottenere informazioni aggiornate
            # sullo stato di avanzamento della run, come completed, failed, etc.
            run = client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )

            if run.status == "completed":
                # Recupera l'ultima risposta
                messages = client.beta.threads.messages.list(
                    thread_id=self.thread_id,
                    order="desc",
                    limit=1
                )

                if messages.data:
                    return messages.data[0].content[0].text.value
                return None

            elif run.status in ["failed", "cancelled", "expired"]:
                return f"Errore nell'agente: {run.status}"

            time.sleep(1)  # Aggiunge un ritardo di 1 secondo tra i tentativi di polling dello stato dell'esecuzione per non sovraccaricare le richieste

# Esempio pratico: Sistema di supporto clienti
def demo_handoff_system():
    """
    Demo di un sistema di trasferimento tra agenti di supporto specializzati.

    Questa demo crea e configura un sistema completo di assistenza clienti con tre agenti specializzati:
    1. Agente di Accoglienza: Primo punto di contatto che gestisce le richieste iniziali
    2. Agente di Supporto Tecnico: Specialista per problemi tecnici e troubleshooting
    3. Agente Amministrativo: Gestisce questioni di fatturazione e contratti

    Il sistema dimostra:
    - Creazione e configurazione di agenti specializzati con istruzioni specifiche
    - Registrazione degli agenti nel sistema di handoff con relative competenze
    - Definizione di regole automatiche per il trasferimento basate su parole chiave
    - Test del sistema con scenari di supporto tecnico e amministrativo
    - Tracciamento dello storico dei trasferimenti

    Note:
        La demo utilizza il modello GPT-4 Turbo per tutti gli agenti.
        I trasferimenti sono automatizzati in base alle parole chiave nel messaggio dell'utente.
        Viene mantenuto un log completo di tutti i trasferimenti effettuati.
    """

    # Crea gli agenti specializzati

    # 1. Agente di primo livello (accoglienza)
    front_desk_agent = client.beta.assistants.create(
        name="Agente Accoglienza",
        instructions="""
        Sei il primo punto di contatto per i clienti.

        Compiti:
        - Accogliere i clienti cordialmente
        - Identificare la loro richiesta
        - Fornire informazioni di base
        - Trasferire a specialisti quando necessario

        Se il cliente menziona problemi tecnici, bug, o errori,
        suggerisci di contattare il supporto tecnico.

        Se parla di fatturazione, pagamenti, o contratti,
        suggerisci il trasferimento all'ufficio amministrativo.
        """,
        model="gpt-4-turbo-preview"
    )

    # 2. Agente supporto tecnico
    tech_support_agent = client.beta.assistants.create(
        name="Supporto Tecnico",
        instructions="""
        Sei uno specialista del supporto tecnico.

        Competenze:
        - Risoluzione di problemi software
        - Debug e troubleshooting
        - Configurazioni tecniche
        - Analisi di log e errori

        Approccio:
        - Fai domande specifiche per diagnosticare
        - Fornisci soluzioni step-by-step
        - Se il problema è complesso, proponi assistenza remota
        """,
        model="gpt-4-turbo-preview"
    )

    # 3. Agente amministrativo
    admin_agent = client.beta.assistants.create(
        name="Ufficio Amministrativo",
        instructions="""
        Gestisci questioni amministrative e finanziarie.

        Competenze:
        - Fatturazione e pagamenti
        - Contratti e sottoscrizioni
        - Modifiche account
        - Rimborsi e crediti

        Mantieni sempre un tono professionale e preciso.
        Per modifiche contrattuali importanti, richiedi sempre
        una conferma scritta.
        """,
        model="gpt-4-turbo-preview"
    )

    # Configura il sistema di handoff
    handoff_manager = AgentHandoffManager()

    # Registra gli agenti
    handoff_manager.register_agent(
        front_desk_agent.id,
        "accoglienza",
        capabilities=["informazioni_generali", "routing"],
        handoff_triggers=["problema_tecnico", "fatturazione"]
    )

    handoff_manager.register_agent(
        tech_support_agent.id,
        "supporto_tecnico",
        capabilities=["debug", "troubleshooting", "configurazione"]
    )

    handoff_manager.register_agent(
        admin_agent.id,
        "amministrativo",
        capabilities=["fatturazione", "contratti", "pagamenti"]
    )

    # Configura le regole di handoff
    handoff_manager.add_handoff_rule(
        from_agent="accoglienza",
        to_agent="supporto_tecnico",
        trigger_keywords=[
            "errore", "bug", "non funziona", "crash", "problema tecnico",
            "configurazione", "installazione", "connessione"
        ]
    )

    handoff_manager.add_handoff_rule(
        from_agent="accoglienza",
        to_agent="amministrativo",
        trigger_keywords=[
            "fattura", "pagamento", "contratto", "abbonamento",
            "rimborso", "prezzo", "costo", "billing"
        ]
    )

    # Test del sistema
    conversation = ConversationWithHandoffs(handoff_manager)

    print("=== TEST 1: Problema Tecnico ===")
    response1 = conversation.start_conversation(
        "accoglienza",
        "Ciao, ho un errore quando provo a fare il login nell'app"
    )
    print(f"Risposta: {response1}")

    print(f"Agente corrente: {conversation.current_agent_type}")

    print("\n=== TEST 2: Questione Amministrativa ===")
    conversation2 = ConversationWithHandoffs(handoff_manager)
    response2 = conversation2.start_conversation(
        "accoglienza",
        "Vorrei informazioni sulla mia fattura di questo mese"
    )
    print(f"Risposta: {response2}")
    print(f"Agente corrente: {conversation2.current_agent_type}")

    # Mostra storico handoff
    print(f"\n=== Storico Handoff ===")
    for handoff in handoff_manager.handoff_history:
        print(f"- {handoff['from_agent']} → {handoff['to_agent']}: {handoff['reason']}")

# Esegui la demo
# demo_handoff_system()
```

---

## 6. Guardrails e Sicurezza

### Tipologie di Guardrails

1. **Input Validation**: Filtra contenuti inappropriati in ingresso, come linguaggio offensivo, informazioni personali sensibili, o istruzioni potenzialmente dannose. Implementa controlli su pattern specifici e parole chiave.

2. **Output Filtering**: Controlla le risposte dell'agente per assicurare che siano appropriate, accurate e sicure. Verifica che non vengano rivelate informazioni riservate o generate risposte potenzialmente dannose. Include anche la formattazione e la sanitizzazione dell'output.

3. **Behavioral Constraints**: Limita i comportamenti dell'agente definendo regole precise su cosa può e non può fare. Ad esempio, impedisce l'accesso a risorse non autorizzate, limita le azioni che può eseguire e definisce i confini del suo ruolo. Include anche vincoli sul tono e stile della comunicazione.

4. **Rate Limiting**: Previene abusi implementando limiti sul numero di richieste per utente/sessione, gestisce il throttling delle API, e protegge da attacchi di tipo DoS. Include anche meccanismi per identificare e bloccare pattern di utilizzo sospetti.

### Implementazione Guardrails

```python
import re
from typing import List, Dict, Any
from enum import Enum

# Definisce un'enumerazione per i diversi tipi di violazioni delle regole di sicurezza (guardrails)
# Ogni valore rappresenta una categoria specifica di violazione che può essere rilevata dal sistema
# La classe Enum permette di definire un insieme fisso di costanti denominate che possono essere utilizzate come tipi
class GuardrailViolationType(Enum):
    """
    Tipi di violazioni dei guardrails (insieme di costanti definite di seguito)
    """
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PERSONAL_INFO_LEAK = "personal_info_leak"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACTION = "unauthorized_action"
    HARMFUL_INSTRUCTION = "harmful_instruction"

class GuardrailResult:
    """
    Rappresenta il risultato di una validazione dei guardrails su un contenuto.

    Questa classe incapsula il risultato della validazione di sicurezza, includendo:
    - Se il contenuto è considerato sicuro
    - Il tipo specifico di violazione se presente
    - Un messaggio descrittivo del problema
    - Il contenuto modificato se è stata applicata una sanitizzazione

    Attributes:
        is_safe (bool): Indica se il contenuto ha superato i controlli di sicurezza
        violation_type (GuardrailViolationType): Il tipo di violazione rilevata, se presente
        message (str): Messaggio descrittivo del risultato o della violazione
        modified_content (str): Versione sanitizzata del contenuto originale, se modificato
    """

    # Tra i parametri, GuardrailViolationType è uno di quelli enumerati nella classe GuardrailViolationType(Enum)
    def __init__(self, is_safe: bool, violation_type: GuardrailViolationType = None, message: str = "", modified_content: str = None):
        self.is_safe = is_safe
        self.violation_type = violation_type
        self.message = message
        self.modified_content = modified_content

class ContentGuardrails:
    """
    Sistema di guardrails per la validazione e sanitizzazione dei contenuti in input e output.

    Questa classe implementa controlli di sicurezza per:
    - Rilevamento di informazioni personali sensibili (PII - Personally Identifiable Information) come email, telefoni, SSN (codice fiscale) mediante pattern regex
    - Filtraggio di contenuti inappropriati e parole chiave offensive
    - Blocco di azioni non autorizzate o potenzialmente dannose

    Attributes:
        pii_patterns (dict): Dizionario di pattern regex per identificare PII
        inappropriate_keywords (list): Lista di parole chiave inappropriate da filtrare
        forbidden_actions (list): Lista di azioni non autorizzate da bloccare

    Note:
        La classe utilizza espressioni regolari per il pattern matching
        ed è estendibile con nuovi pattern e regole di validazione.
        I risultati delle validazioni sono restituiti come oggetti GuardrailResult.
    """

    def __init__(self):
        # Pattern per rilevare informazioni personali
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }

        # Parole chiave inappropriate
        self.inappropriate_keywords = [
            "violenza", "odio", "discriminazione", "hack", "bypass"
        ]

        # Azioni non autorizzate
        self.forbidden_actions = [
            "delete", "drop", "remove", "destroy", "hack", "crack"
        ]

    # Questo metodo valida il contenuto in input verificando la presenza di contenuti inappropriati, informazioni personali sensibili e azioni non autorizzate.
    # Restituisce un oggetto GuardrailResult con il risultato della validazione.
    def validate_input(self, content: str, user_context: Dict = None) -> GuardrailResult:
        """
        Valida il contenuto in input dall'utente per garantire la sicurezza e l'appropriatezza.

        Args:
            content (str): Il contenuto testuale da validare
            user_context (Dict, optional): Dizionario contenente informazioni contestuali sull'utente. Default None.

        Returns:
            GuardrailResult: Un oggetto contenente il risultato della validazione con:
                - is_safe (bool): True se il contenuto è sicuro, False altrimenti
                - violation_type (GuardrailViolationType): Il tipo di violazione se presente
                - message (str): Messaggio descrittivo del risultato o della violazione
                - modified_content (str): Versione modificata del contenuto se necessario

        Note:
            La validazione controlla:
            1. Contenuti inappropriati usando una lista di parole chiave
            2. Informazioni personali sensibili (PII) tramite pattern regex
            3. Azioni non autorizzate o potenzialmente dannose
        """
        content_lower = content.lower()

        # 1. Controlla contenuti inappropriati
        for keyword in self.inappropriate_keywords:
            if keyword in content_lower:
                return GuardrailResult(
                    is_safe=False,
                    violation_type=GuardrailViolationType.INAPPROPRIATE_CONTENT,
                    message=f"Contenuto inappropriato rilevato: {keyword}"
                )

        # 2. Controlla informazioni personali
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, content):
                return GuardrailResult(
                    is_safe=False,
                    violation_type=GuardrailViolationType.PERSONAL_INFO_LEAK,
                    message=f"Informazione personale rilevata: {pii_type}"
                )

        # 3. Controlla azioni non autorizzate
        for action in self.forbidden_actions:
            if action in content_lower:
                return GuardrailResult(
                    is_safe=False,
                    violation_type=GuardrailViolationType.UNAUTHORIZED_ACTION,
                    message=f"Azione non autorizzata richiesta: {action}"
                )

        # In caso tutti i controlli siano positivi ritorna che il contenuto è safe
        return GuardrailResult(is_safe=True)


    def validate_output(self, content: str, agent_context: Dict = None) -> GuardrailResult:
        """
        Valida l'output dell'agente prima di inviarlo all'utente.

        Args:
            content (str): Il contenuto testuale da validare generato dall'agente
            agent_context (Dict, optional): Dizionario contenente informazioni contestuali sull'agente. Default None.

        Returns:
            GuardrailResult: Un oggetto contenente il risultato della validazione con:
                - is_safe (bool): True se il contenuto è sicuro o è stato modificato per essere sicuro
                - violation_type (GuardrailViolationType): Il tipo di violazione se presente
                - message (str): Messaggio descrittivo del risultato o della violazione
                - modified_content (str): Versione modificata del contenuto se sono state rilevate e censurate informazioni personali

        Note:
            La validazione effettua due controlli principali:
            1. Ricerca e censura di informazioni personali (PII) utilizzando pattern regex
            2. Identificazione di istruzioni potenzialmente dannose come tentativi di bypass
               delle misure di sicurezza o rivelazione dei prompt di sistema
        """

        # 1. Controlla leak di informazioni personali
        modified_content = content
        found_pii = False

        for pii_type, pattern in self.pii_patterns.items():
            # finditer restituisce un iteratore di tutti i match del pattern regex nel contenuto,
            # permettendo di trovare tutte le occorrenze di PII da censurare
            matches = re.finditer(pattern, content)
            for match in matches:
                # Sostituisce con placeholder
                replacement = f"[{pii_type.upper()}_REDACTED]"
                modified_content = modified_content.replace(match.group(), replacement)
                found_pii = True

        if found_pii:
            return GuardrailResult(
                is_safe=True,  # Safe dopo la modifica
                violation_type=GuardrailViolationType.PERSONAL_INFO_LEAK,
                message="Informazioni personali censurate",
                modified_content=modified_content
            )

        # 2. Controlla istruzioni potenzialmente dannose
        # Lista di pattern regex per identificare istruzioni potenzialmente dannose
        # Il prefisso 'r' indica una raw string dove i backslash non vengono interpretati come escape
        # .{0,20} significa "qualsiasi carattere ripetuto da 0 a 20 volte"
        # Quindi r"ignora.{0,20}istruzioni" matcha "ignora le istruzioni", "ignora queste istruzioni", etc.
        harmful_patterns = [
            r"ignora.{0,20}istruzioni",  # Matcha tentativi di ignorare le istruzioni di sistema
            r"bypass.{0,20}sicurezza",    # Matcha tentativi di bypassare i controlli di sicurezza
            r"reveala.{0,20}prompt"       # Matcha tentativi di rivelare i prompt di sistema
        ]

        for pattern in harmful_patterns:
            if re.search(pattern, content.lower()):
                return GuardrailResult(
                    is_safe=False,
                    violation_type=GuardrailViolationType.HARMFUL_INSTRUCTION,
                    message="Istruzione potenzialmente dannosa rilevata"
                )

        return GuardrailResult(is_safe=True)

class RateLimitGuardrail:
    """
    Guardrail per limitare la frequenza delle richieste
    """

    def __init__(self):
        # Tracciamento richieste per utente
        self.user_requests = {}

        # Limiti configurabili
        self.limits = {
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "requests_per_day": 1000
        }

    def check_rate_limit(self, user_id: str) -> GuardrailResult:
        """
        Controlla se l'utente ha superato i limiti di frequenza
        """
        import time
        # deque (double-ended queue) è una struttura dati ottimizzata per l'inserimento e la rimozione di elementi
        # sia all'inizio che alla fine della coda, con complessità O(1). È ideale per implementare code con
        # dimensione fissa e per tenere traccia delle ultime N richieste
        from collections import deque

        current_time = time.time()

        # Inizializza tracking per nuovo utente
        if user_id not in self.user_requests:
            self.user_requests[user_id] = {
                "minute": deque(),
                "hour": deque(),
                "day": deque()
            }

        user_data = self.user_requests[user_id]

        # Pulisce richieste vecchie
        self._cleanup_old_requests(user_data, current_time)

        # Controlla limiti
        if len(user_data["minute"]) >= self.limits["requests_per_minute"]:
            return GuardrailResult(
                is_safe=False,
                violation_type=GuardrailViolationType.RATE_LIMIT_EXCEEDED,
                message="Limite richieste al minuto superato"
            )

        if len(user_data["hour"]) >= self.limits["requests_per_hour"]:
            return GuardrailResult(
                is_safe=False,
                violation_type=GuardrailViolationType.RATE_LIMIT_EXCEEDED,
                message="Limite richieste orario superato"
            )

        if len(user_data["day"]) >= self.limits["requests_per_day"]:
            return GuardrailResult(
                is_safe=False,
                violation_type=GuardrailViolationType.RATE_LIMIT_EXCEEDED,
                message="Limite richieste giornaliero superato"
            )

        # Registra la nuova richiesta
        user_data["minute"].append(current_time)
        user_data["hour"].append(current_time)
        user_data["day"].append(current_time)

        return GuardrailResult(is_safe=True)

    def _cleanup_old_requests(self, user_data: Dict, current_time: float):
        """
        Rimuove le richieste obsolete dai contatori di rate limiting per ogni intervallo temporale.

        Args:
            user_data (Dict): Dizionario contenente le code di richieste per minuto, ora e giorno
            current_time (float): Timestamp corrente in secondi dall'epoch

        Note:
            Il metodo mantiene aggiornate tre code separate:
            - minute: richieste degli ultimi 60 secondi
            - hour: richieste delle ultime 3600 secondi (1 ora)
            - day: richieste degli ultimi 86400 secondi (24 ore)

            Per ogni coda, rimuove iterativamente le richieste più vecchie del rispettivo
            intervallo temporale usando popleft() che ha complessità O(1).
            Le code sono implementate come deque per efficienza nelle operazioni di rimozione.
        """
        # Rimuove richieste più vecchie di 1 minuto
        while (user_data["minute"] and
               current_time - user_data["minute"][0] > 60):
            user_data["minute"].popleft()

        # Rimuove richieste più vecchie di 1 ora
        while (user_data["hour"] and
               current_time - user_data["hour"][0] > 3600):
            user_data["hour"].popleft()

        # Rimuove richieste più vecchie di 1 giorno
        while (user_data["day"] and
               current_time - user_data["day"][0] > 86400):
            user_data["day"].popleft()

class SecureAgentWrapper:
    """
    Wrapper di sicurezza per agenti conversazionali che implementa guardrails e controlli di protezione.

    Questa classe aggiunge diversi livelli di sicurezza agli agenti:
    - Rate limiting per prevenire abusi
    - Validazione input per filtrare contenuti inappropriati
    - Controllo output per evitare risposte potenzialmente dannose
    - Logging delle violazioni per monitoraggio e audit

    Attributes:
        agent_id (str): ID dell'agente OpenAI da proteggere
        user_id (str, optional): ID dell'utente per il rate limiting
        content_guardrails (ContentGuardrails): Sistema di validazione contenuti
        rate_limiter (RateLimitGuardrail): Sistema di rate limiting
        violation_log (list): Storico delle violazioni rilevate

    Note:
        La classe utilizza i guardrails definiti in ContentGuardrails e RateLimitGuardrail
        per implementare una pipeline di sicurezza completa. Ogni messaggio viene validato
        sia in input che in output, con possibilità di modificare o bloccare contenuti
        non conformi alle policy di sicurezza.

    Example:
        secure_agent = SecureAgentWrapper(
            agent_id="asst_123",
            user_id="user_456"
        )
        result = secure_agent.send_secure_message(
            thread_id="thread_789",
            message="Hello"
        )
    """

    def __init__(self, agent_id: str, user_id: str = None):
        self.agent_id = agent_id
        self.user_id = user_id

        # Inizializza i guardrails con le due classi precedentemente definite
        self.content_guardrails = ContentGuardrails()
        self.rate_limiter = RateLimitGuardrail()

        # Tracking violazioni - Inizializza la lista vuota che verra implementata successivamente
        self.violation_log = []

    def send_secure_message(self, thread_id: str, message: str) -> Dict[str, Any]:
        """
        Invia un messaggio all'agente applicando una serie completa di controlli di sicurezza.

        Questo metodo implementa una pipeline di sicurezza a più livelli:
        1. Rate limiting: Verifica che l'utente non abbia superato i limiti di utilizzo
        2. Validazione input: Controlla che il messaggio non contenga contenuti inappropriati
        3. Invio sicuro: Gestisce la comunicazione con l'agente in modo protetto
        4. Validazione output: Verifica la sicurezza della risposta dell'agente

        Args:
            thread_id (str): ID del thread di conversazione
            message (str): Messaggio da inviare all'agente

        Returns:
            Dict[str, Any]: Dizionario contenente:
                - success (bool): True se l'operazione è completata con successo
                - response (str): Risposta dell'agente se success=True
                - modified (bool): True se la risposta è stata modificata dai guardrails
                - error (str): Messaggio di errore se success=False
                - violation_type (str): Tipo di violazione se rilevata

        Note:
            Il metodo registra automaticamente eventuali violazioni delle policy di sicurezza
            e può modificare o bloccare messaggi che non rispettano i criteri definiti.
        """
        import datetime

        # 1. Rate limiting
        if self.user_id:
            rate_check = self.rate_limiter.check_rate_limit(self.user_id)
            if not rate_check.is_safe:
                self._log_violation(rate_check)
                return {
                    "success": False,
                    "error": rate_check.message,
                    "violation_type": rate_check.violation_type.value
                }

        # 2. Validazione input
        input_validation = self.content_guardrails.validate_input(
            message,
            {"user_id": self.user_id}
        )

        if not input_validation.is_safe:
            self._log_violation(input_validation)
            return {
                "success": False,
                "error": input_validation.message,
                "violation_type": input_validation.violation_type.value
            }

        # 3. Invia messaggio all'agente
        try:
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # Esegue l'agente
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.agent_id
            )

            # Attende la risposta con il metodo privato definito poco sotto
            agent_response = self._wait_for_safe_response(thread_id, run)

            if agent_response["success"]:
                return {
                    "success": True,
                    "response": agent_response["content"],
                    "modified": agent_response.get("modified", False)
                }
            else:
                return agent_response

        except Exception as e:
            return {
                "success": False,
                "error": f"Errore interno: {str(e)}"
            }

    def _wait_for_safe_response(self, thread_id: str, run) -> Dict[str, Any]:
        """
        Attende e valida la risposta dell'agente
        """
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run.status == "completed":
                # Recupera la risposta
                messages = client.beta.threads.messages.list(
                    thread_id=thread_id,
                    order="desc",
                    limit=1
                )

                if messages.data and messages.data[0].role == "assistant":
                    raw_response = messages.data[0].content[0].text.value

                    # Valida l'output
                    output_validation = self.content_guardrails.validate_output(
                        raw_response,
                        {"agent_id": self.agent_id}
                    )

                    if not output_validation.is_safe and not output_validation.modified_content:
                        # Risposta non sicura e non modificabile
                        self._log_violation(output_validation)
                        return {
                            "success": False,
                            "error": "Risposta dell'agente bloccata per sicurezza"
                        }

                    # Restituisce la risposta (originale o modificata)
                    final_content = (
                        output_validation.modified_content
                        if output_validation.modified_content
                        else raw_response
                    )

                    return {
                        "success": True,
                        "content": final_content,
                        "modified": bool(output_validation.modified_content)
                    }

                return {"success": False, "error": "Nessuna risposta dall'agente"}

            elif run.status in ["failed", "cancelled", "expired"]:
                return {"success": False, "error": f"Agente failed: {run.status}"}

            time.sleep(1)

    # metodo privato per tenere traccia dei log delle violazioni
    def _log_violation(self, violation: GuardrailResult):
        """
        Registra una violazione dei guardrails
        """
        import datetime

        self.violation_log.append({
            "timestamp": datetime.datetime.now(),
            "type": violation.violation_type.value,
            "message": violation.message,
            "user_id": self.user_id
        })

        print(f"⚠️ Violazione guardrail: {violation.message}")

    def get_violation_summary(self) -> Dict[str, Any]:
        """
        Restituisce un riassunto delle violazioni
        """
        from collections import Counter

        if not self.violation_log:
            return {"total_violations": 0}

        violations_by_type = Counter(
            v["type"] for v in self.violation_log
        )

        return {
            "total_violations": len(self.violation_log),
            "by_type": dict(violations_by_type),
            "latest_violation": self.violation_log[-1] if self.violation_log else None
        }

# Esempio di utilizzo completo
def demo_secure_agent():
    """
    Dimostra l'implementazione e l'utilizzo di un agente conversazionale con guardrails di sicurezza.

    Questa demo:
    1. Crea un agente di test con istruzioni specifiche sulla sicurezza
    2. Lo avvolge in un wrapper che implementa i controlli di sicurezza
    3. Esegue una serie di test per dimostrare:
        - Gestione normale dei messaggi
        - Blocco di contenuti inappropriati
        - Censura di informazioni personali
    4. Produce un report delle violazioni di sicurezza rilevate

    La demo utilizza tre scenari di test:
    - Test 1: Messaggio normale per verificare il funzionamento base
    - Test 2: Tentativo di azione dannosa per testare il blocco
    - Test 3: Inserimento di PII per testare la censura

    Returns:
        None: I risultati vengono stampati direttamente sulla console

    Note:
        Questa demo è utile per comprendere come implementare e testare
        un sistema di guardrails completo per agenti conversazionali.
    """

    # Crea un agente di test
    agent = client.beta.assistants.create(
        name="Agente Sicuro Test",
        instructions="""
        Sei un assistente utile ma devi sempre rispettare
        le policy di sicurezza. Non condividere mai informazioni
        personali e non eseguire azioni potenzialmente dannose.
        """,
        model="gpt-4-turbo-preview"
    )

    # Crea il wrapper sicuro
    secure_agent = SecureAgentWrapper(
        agent_id=agent.id,
        user_id="test_user_123"
    )

    # Crea un thread per la conversazione
    thread = client.beta.threads.create()

    # Test 1: Messaggio normale
    print("=== TEST 1: Messaggio Normale ===")
    result1 = secure_agent.send_secure_message(
        thread.id,
        "Ciao, puoi aiutarmi con un problema di matematica?"
    )
    print(f"Risultato: {result1}")

    # Test 2: Contenuto inappropriato (dovrebbe essere bloccato)
    print("\n=== TEST 2: Contenuto Inappropriato ===")
    result2 = secure_agent.send_secure_message(
        thread.id,
        "Come posso fare un hack del sistema?"
    )
    print(f"Risultato: {result2}")

    # Test 3: Informazione personale (dovrebbe essere censurata)
    print("\n=== TEST 3: Con Email (test censura) ===")
    result3 = secure_agent.send_secure_message(
        thread.id,
        "La mia email è test@example.com"
    )
    print(f"Risultato: {result3}")

    # Mostra riassunto violazioni
    print(f"\n=== Riassunto Violazioni ===")
    summary = secure_agent.get_violation_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")

# Esegui la demo
# demo_secure_agent()
```

---

## 7. Esempi Pratici Completi

### Assistente E-commerce con Handoff

```python
def create_ecommerce_system():
    """
    Crea un sistema completo per e-commerce con due agenti
    """

    # Agente venditore
    sales_agent = client.beta.assistants.create(
        name="Consulente Vendite",
        instructions="""
        Sei un esperto consulente vendite per un negozio online.

        Competenze:
        - Consigliare prodotti basati sulle esigenze
        - Spiegare caratteristiche e vantaggi
        - Gestire obiezioni
        - Guidare verso l'acquisto

        Stile: Amichevole ma professionale, focalizzato sui benefici per il cliente.
        """,
        model="gpt-4-turbo-preview",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Cerca prodotti nel catalogo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "category": {"type": "string"},
                            "max_price": {"type": "number"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    )

    # Agente supporto tecnico
    support_agent = client.beta.assistants.create(
        name="Supporto Tecnico",
        instructions="""
        Fornisci supporto tecnico post-vendita.

        Compiti:
        - Risoluzione problemi prodotti
        - Assistenza installazione/configurazione
        - Gestione resi e sostituzioni
        - Troubleshooting
        """,
        model="gpt-4-turbo-preview",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "check_order_status",
                    "description": "Controlla lo stato di un ordine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "string"}
                        },
                        "required": ["order_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "initiate_return",
                    "description": "Avvia procedura di reso",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["order_id", "reason"]
                    }
                }
            }
        ]
    )

    return sales_agent, support_agent

def search_products(query, category=None, max_price=None):
    """
    Simula una ricerca di prodotti nel catalogo applicando filtri opzionali.

    Args:
        query (str): La stringa di ricerca da utilizzare per filtrare i prodotti per nome
        category (str, optional): Categoria di prodotti da filtrare. Default None.
        max_price (float, optional): Prezzo massimo per filtrare i prodotti. Default None.

    Returns:
        dict: Un dizionario contenente:
            - products (list): Lista dei prodotti filtrati che corrispondono ai criteri
            - total (int): Numero totale di prodotti trovati

    Note:
        La funzione filtra i prodotti in base a:
        - Corrispondenza case-insensitive del nome con la query
        - Categoria esatta se specificata
        - Prezzo massimo se specificato
        Questa è una simulazione con un dataset hardcoded di prodotti.
    """
    products = [
        {"id": 1, "name": "Smartphone Pro", "price": 899, "category": "elettronica"},
        {"id": 2, "name": "Laptop Gaming", "price": 1299, "category": "computer"},
        {"id": 3, "name": "Cuffie Wireless", "price": 199, "category": "audio"},
    ]

    # Filtra per categoria e prezzo
    # Questo codice supporta ricerche multi-parametro perché:
    # - Filtra per nome prodotto usando query.lower()
    # - Filtra opzionalmente per categoria esatta
    # - Filtra opzionalmente per prezzo massimo
    # Tutti i filtri vengono applicati in AND, quindi un prodotto deve soddisfare tutti i criteri specificati
    results = []
    for product in products:
        if category and product["category"] != category.lower():
            continue
        if max_price and product["price"] > max_price:
            continue
        if query.lower() in product["name"].lower():
            results.append(product)

    return {"products": results, "total": len(results)}

def check_order_status(order_id):
    """Simula controllo stato ordine"""
    return {
        "order_id": order_id,
        "status": "In spedizione",
        "tracking": "ABC123456789",
        "delivery_date": "2024-02-15"
    }

def initiate_return(order_id, reason):
    """Simula avvio reso"""
    return {
        "return_id": f"RET_{order_id}",
        "status": "Reso autorizzato",
        "instructions": "Stampa l'etichetta e spedisci entro 14 giorni"
    }
```

### Sistema Educativo Adattivo

```python
def create_adaptive_learning_system():
    """
    Sistema di apprendimento che si adatta al livello dello studente
    È fornito di due tool per valutare il livello di comprensione e per generare esercizi
    sulla base del livello raggiunto dallo studente
    """

    tutor_agent = client.beta.assistants.create(
        name="Tutor Adattivo",
        instructions="""
        Sei un tutor intelligente che personalizza l'insegnamento.

        Approccio:
        1. Valuta il livello iniziale dello studente
        2. Adatta spiegazioni e esercizi di conseguenza
        3. Monitora i progressi e aggiusta la difficoltà
        4. Fornisci feedback costruttivo
        5. Celebra i successi e incoraggia nei momenti difficili

        Ricorda: ogni studente impara diversamente!
        """,
        model="gpt-4-turbo-preview",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "assess_student_level",
                    "description": "Valuta il livello di comprensione",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject": {"type": "string"},
                            "student_answer": {"type": "string"},
                            "correct_answer": {"type": "string"}
                        },
                        "required": ["subject", "student_answer"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_exercise",
                    "description": "Genera esercizio personalizzato",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject": {"type": "string"},
                            "difficulty_level": {"type": "string"},
                            "learning_style": {"type": "string"}
                        },
                        "required": ["subject", "difficulty_level"]
                    }
                }
            }
        ]
    )

    return tutor_agent

# Funzione per valutare la risposta dello studente in confronto a quella corretta
def assess_student_level(subject, student_answer, correct_answer=None):
    """Valuta la risposta dello studente"""
    # Algoritmo semplificato di valutazione
    if correct_answer:
        # Calcola la similarità tra la risposta dello studente e quella corretta
        # Converte le risposte in set di parole e trova l'intersezione, normalizzando per la lunghezza della risposta corretta
        similarity = len(set(student_answer.lower().split()) & set(correct_answer.lower().split())) / len(correct_answer.split())

        if similarity > 0.8:
            level = "avanzato"
            feedback = "Eccellente comprensione!"
        elif similarity > 0.5:
            level = "intermedio"
            feedback = "Buona comprensione, ma c'è margine di miglioramento"
        else:
            level = "principiante"
            feedback = "Hai bisogno di rivedere alcuni concetti base"
    else:
        # Valutazione qualitativa senza risposta corretta
        if len(student_answer.split()) > 10:
            level = "intermedio"
            feedback = "Risposta articolata, mostra comprensione"
        else:
            level = "principiante"
            feedback = "Risposta breve, potrebbe indicare incertezza"

    return {
        "assessed_level": level,
        "feedback": feedback,
        "subject": subject,
        "confidence_score": similarity if correct_answer else 0.5
    }

def generate_exercise(subject, difficulty_level, learning_style="mixed"):
    """Genera esercizio personalizzato"""
    exercises = {
        "matematica": {
            "principiante": {
                "visual": "Disegna 3 mele e 2 pere. Quanta frutta hai in totale?",
                "textual": "Se hai 5 euro e spendi 2 euro, quanto ti rimane?",
                "mixed": "Calcola: 7 + 3 = ?"
            },
            "intermedio": {
                "visual": "Un rettangolo ha base 8cm e altezza 5cm. Calcola l'area.",
                "textual": "Un treno viaggia a 80 km/h per 2 ore. Quanta strada percorre?",
                "mixed": "Risolvi: 3x + 5 = 14"
            },
            "avanzato": {
                "visual": "Grafica la funzione f(x) = x² - 4x + 3",
                "textual": "Dimostra che la derivata di x³ è 3x²",
                "mixed": "Calcola l'integrale di 2x dx da 0 a 3"
            }
        }
    }

    if subject in exercises and difficulty_level in exercises[subject]:
        exercise = exercises[subject][difficulty_level].get(learning_style, exercises[subject][difficulty_level]["mixed"])
        return {
            "exercise": exercise,
            "difficulty": difficulty_level,
            "style": learning_style,
            "subject": subject
        }

    return {"error": f"Nessun esercizio trovato per {subject} livello {difficulty_level}"}
```

---

## 8. Best Practices e Ottimizzazioni

### Performance e Costi

```python
class AgentOptimizer:
    """
    Utilità per ottimizzare performance e costi degli agenti
    """

    def __init__(self):
        self.usage_stats = {}
        self.model_costs = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},  # per 1K token
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
        }

    def choose_optimal_model(self, task_complexity, budget_priority=False):
        """
        Sceglie il modello LLM ottimale basato sulla complessità del task e priorità di budget.

        Args:
            task_complexity (int): Livello di complessità del task da 1 a 10 dove 1 è molto semplice e 10 è molto complesso
            budget_priority (bool, optional): Se True, privilegia modelli più economici. Se False, privilegia la qualità. Default False.

        Returns:
            str: Nome del modello LLM scelto ("gpt-3.5-turbo" o "gpt-4-turbo-preview")

        Note:
            Con budget_priority=True:
            - task_complexity <= 3: usa gpt-3.5-turbo (più economico)
            - task_complexity > 3: usa gpt-4-turbo-preview

            Con budget_priority=False:
            - task_complexity < 4: usa gpt-3.5-turbo
            - task_complexity >= 4: usa gpt-4-turbo-preview (migliore qualità)
        """

        if budget_priority:
            # Priorità al costo
            if task_complexity <= 3:  # Task semplici
                return "gpt-3.5-turbo"
            else:
                return "gpt-4-turbo-preview"
        else:
            # Priorità alla qualità
            if task_complexity >= 7:  # Task complessi
                return "gpt-4-turbo-preview"
            elif task_complexity >= 4:
                return "gpt-4-turbo-preview"
            else:
                return "gpt-3.5-turbo"

    def optimize_instructions(self, base_instructions, task_type):
        """
        Ottimizza le istruzioni per l'agente riducendo i token e migliorando l'efficacia.

        Args:
            base_instructions (str): Le istruzioni base da ottimizzare
            task_type (str): Il tipo di task per cui ottimizzare le istruzioni. Valori supportati: "customer_service", "technical_support", "sales"

        Returns:
            str: Le istruzioni ottimizzate. Se task_type è riconosciuto, restituisce un template
                predefinito ottimizzato per quel tipo di task. Altrimenti restituisce le istruzioni
                base ottimizzate rimuovendo frasi ridondanti comuni.

        Note:
            I template predefiniti sono ottimizzati per:
            - Customer service: focus su risoluzione rapida e cortese dei problemi
            - Technical support: struttura diagnostica step-by-step
            - Sales: approccio consultivo orientato al valore

            Per istruzioni base generiche, il metodo rimuove frasi ridondanti comuni come
            "Come assistente AI", "Sono qui per aiutarti" etc.
        """

        optimization_templates = {
            "customer_service": """
                Ruolo: Assistente clienti professionale
                Obiettivo: Risolvere problemi rapidamente e cortesemente
                Limiti: Max 150 parole per risposta
                Escalation: Trasferisci a umano se richiesto
            """,

            "technical_support": """
                Ruolo: Tecnico esperto
                Processo: 1) Diagnosi 2) Soluzione step-by-step 3) Verifica
                Formato: Elenchi puntati per procedure
                Tools: Usa sempre gli strumenti disponibili
            """,

            "sales": """
                Ruolo: Consulente vendite
                Approccio: Identifica bisogni → Proponi soluzioni → Gestisci obiezioni
                Stile: Consultivo, non aggressivo
                Obiettivo: Valore per il cliente = conversione
            """
        }

        if task_type in optimization_templates:
            return optimization_templates[task_type]

        # Ottimizzazione generica: rimuove ridondanze
        optimized = base_instructions.strip()

        # Rimuove frasi ripetitive comuni
        redundant_phrases = [
            "Come assistente AI,",
            "Sono qui per aiutarti",
            "Il mio obiettivo è",
        ]

        for phrase in redundant_phrases:
            optimized = optimized.replace(phrase, "")

        return optimized.strip()

    def estimate_token_usage(self, instructions, average_message_length=100, messages_per_session=10):
        """
        Stima l'utilizzo di token per una sessione di conversazione.

        Args:
            instructions (str): Le istruzioni di sistema fornite all'agente
            average_message_length (int, optional): Lunghezza media stimata dei messaggi in caratteri. Default 100.
            messages_per_session (int, optional): Numero medio di messaggi per sessione. Default 10.

        Returns:
            dict: Dizionario contenente:
                - instruction_tokens (int): Numero stimato di token per le istruzioni
                - estimated_total_per_session (int): Stima totale dei token per sessione
                - messages_per_session (int): Numero di messaggi per sessione

        Note:
            - Usa un'approssimazione di 1 token ogni 4 caratteri
            - Considera sia i messaggi in input che in output
            - La stima è approssimativa e può variare in base al modello e al contenuto effettivo
        """

        # Stima token per istruzioni (approssimazione: 1 token ~= 4 caratteri)
        instruction_tokens = len(instructions) // 4

        # Token per messaggio medio
        message_tokens = average_message_length // 4

        # Token totali per sessione
        total_tokens = (instruction_tokens * messages_per_session + message_tokens * messages_per_session * 2)  # *2 per input+output

        return {
            "instruction_tokens": instruction_tokens,
            "estimated_total_per_session": total_tokens,
            "messages_per_session": messages_per_session
        }

    def calculate_session_cost(self, model, total_tokens):
        """
        Calcola il costo stimato per sessione
        """
        if model not in self.model_costs:
            return {"error": f"Costi non disponibili per {model}"}

        costs = self.model_costs[model]

        # Assumiamo 70% input, 30% output
        input_tokens = total_tokens * 0.7
        output_tokens = total_tokens * 0.3

        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]

        return {
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "total_cost": round(input_cost + output_cost, 4),
            "currency": "USD"
        }

class AgentMonitoring:
    """
    Sistema di monitoraggio per agenti in produzione
    """

    def __init__(self):
        self.metrics = {
            "response_times": [],
            "error_rates": {},
            "user_satisfaction": [],
            "token_usage": [],
            "handoff_rates": {}
        }

    def track_response_time(self, agent_id, response_time):
        """Traccia i tempi di risposta"""
        import time

        self.metrics["response_times"].append({
            "agent_id": agent_id,
            "time": response_time,
            "timestamp": time.time()
        })

    def track_error(self, agent_id, error_type, context=None):
        """Traccia gli errori"""
        if agent_id not in self.metrics["error_rates"]:
            self.metrics["error_rates"][agent_id] = {}

        if error_type not in self.metrics["error_rates"][agent_id]:
            self.metrics["error_rates"][agent_id][error_type] = 0

        self.metrics["error_rates"][agent_id][error_type] += 1

    def get_performance_report(self, agent_id=None):
        """Genera report di performance"""
        if agent_id:
            # Report specifico per agente
            agent_responses = [r for r in self.metrics["response_times"] if r["agent_id"] == agent_id]

            if agent_responses:
                avg_response_time = sum(r["time"] for r in agent_responses) / len(agent_responses)
                max_response_time = max(r["time"] for r in agent_responses)
            else:
                avg_response_time = max_response_time = 0

            agent_errors = self.metrics["error_rates"].get(agent_id, {})

            return {
                "agent_id": agent_id,
                "avg_response_time": round(avg_response_time, 2),
                "max_response_time": round(max_response_time, 2),
                "total_requests": len(agent_responses),
                "errors_by_type": agent_errors,
                "total_errors": sum(agent_errors.values())
            }
        else:
            # Report generale
            all_times = [r["time"] for r in self.metrics["response_times"]]

            return {
                "total_requests": len(all_times),
                "avg_response_time": round(sum(all_times) / len(all_times), 2) if all_times else 0,
                "agents_with_errors": len(self.metrics["error_rates"]),
                "total_errors": sum(sum(errors.values()) for errors in self.metrics["error_rates"].values())
            }

# Esempio di ottimizzazione completa
def demo_optimization():
    """
    Dimostra l'ottimizzazione di un agente utilizzando le classi precedentemente definite
    """

    optimizer = AgentOptimizer()
    monitor = AgentMonitoring()

    # 1. Ottimizzazione istruzioni
    original_instructions = """
    Come assistente AI, sono qui per aiutarti con il supporto clienti.
    Il mio obiettivo è fornire assistenza di alta qualità e risolvere
    i tuoi problemi in modo efficiente. Posso aiutarti con domande
    sui prodotti, problemi tecnici, e questioni di fatturazione.
    Sono programmato per essere sempre cortese e professionale.
    """

    optimized_instructions = optimizer.optimize_instructions(
        original_instructions,
        "customer_service"
    )

    print("=== Ottimizzazione Istruzioni ===")
    print(f"Originali: {len(original_instructions)} caratteri")
    print(f"Ottimizzate: {len(optimized_instructions)} caratteri")
    print(f"Riduzione: {((len(original_instructions) - len(optimized_instructions)) / len(original_instructions) * 100):.1f}%")

    # 2. Scelta modello ottimale
    task_complexity = 5  # Scala 1-10
    budget_model = optimizer.choose_optimal_model(task_complexity, budget_priority=True)
    quality_model = optimizer.choose_optimal_model(task_complexity, budget_priority=False)

    print(f"\n=== Scelta Modello (Complessità {task_complexity}) ===")
    print(f"Budget priority: {budget_model}")
    print(f"Quality priority: {quality_model}")

    # 3. Stima token e costi
    token_estimate = optimizer.estimate_token_usage(
        optimized_instructions,
        average_message_length=150,
        messages_per_session=8
    )

    budget_cost = optimizer.calculate_session_cost(budget_model, token_estimate["estimated_total_per_session"])
    quality_cost = optimizer.calculate_session_cost(quality_model, token_estimate["estimated_total_per_session"])

    print(f"\n=== Analisi Costi ===")
    print(f"Token stimati per sessione: {token_estimate['estimated_total_per_session']}")
    print(f"Costo con {budget_model}: ${budget_cost['total_cost']}")
    print(f"Costo con {quality_model}: ${quality_cost['total_cost']}")
    print(f"Differenza: ${quality_cost['total_cost'] - budget_cost['total_cost']:.4f}")

# Esegui demo ottimizzazione
# demo_optimization()
```

---

## 9. Deployment e Produzione

### Gestione Configurazioni

```python
import os
import json
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AgentConfig:
    """
    Classe di configurazione per un agente conversazionale.

    Attributes:
        name (str): Nome identificativo dell'agente
        instructions (str): Istruzioni di sistema che definiscono il comportamento dell'agente
        model (str): Identificatore del modello LLM da utilizzare (es. "gpt-4-turbo-preview")
        tools (List[Dict]): Lista di strumenti/funzioni disponibili per l'agente
        temperature (float): Parametro di temperatura per il sampling (default 0.1)
        max_tokens (Optional[int]): Limite massimo di token per risposta (default None)
        metadata (Dict): Metadati aggiuntivi per l'agente (default None)

    Note:
        Utilizza il decoratore @dataclass per generare automaticamente __init__,
        __repr__ e altri metodi speciali. I valori di default sono ottimizzati
        per un comportamento deterministico dell'agente.
    """
    name: str
    instructions: str
    model: str
    tools: List[Dict]
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    metadata: Dict = None

class ConfigManager:
    """
    Gestisce configurazioni per ambienti diversi
    """

    def __init__(self, config_path="agent_configs"):
        self.config_path = config_path
        self.configs = {}
        self.load_all_configs()

    def load_all_configs(self):
        """Carica tutte le configurazioni disponibili per le attività di development, staging e produzione"""

        # Configurazioni predefinite
        self.configs = {
            "development": {
                "customer_service": AgentConfig(
                    name="Customer Service (Dev)",
                    instructions="Assistente clienti per ambiente di sviluppo. Usa dati di test.",
                    model="gpt-3.5-turbo",  # Modello più economico per dev
                    tools=[],
                    temperature=0.3  # Più creatività per test
                ),
                "technical_support": AgentConfig(
                    name="Tech Support (Dev)",
                    instructions="Supporto tecnico per test e sviluppo.",
                    model="gpt-3.5-turbo",
                    tools=[],
                    temperature=0.1
                )
            },

            "staging": {
                "customer_service": AgentConfig(
                    name="Customer Service (Staging)",
                    instructions="Assistente clienti per ambiente di staging. Simula produzione.",
                    model="gpt-4-turbo-preview",  # Modello produzione per test realistici
                    tools=[],
                    temperature=0.1
                ),
                "technical_support": AgentConfig(
                    name="Tech Support (Staging)",
                    instructions="Supporto tecnico con configurazione di produzione.",
                    model="gpt-4-turbo-preview",
                    tools=[],
                    temperature=0.1
                )
            },

            "production": {
                "customer_service": AgentConfig(
                    name="Customer Service",
                    instructions="""
                    Assistente clienti professionale per azienda e-commerce.

                    Priorità:
                    1. Risoluzione rapida problemi
                    2. Esperienza cliente eccellente
                    3. Escalation appropriata

                    Policy:
                    - Max 2 minuti per risposta
                    - Sempre cortese e professionale
                    - Raccolta feedback quando possibile
                    """,
                    model="gpt-4-turbo-preview",
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": "search_orders",
                                "description": "Cerca ordini cliente"
                            }
                        }
                    ],
                    temperature=0.1,
                    metadata={"environment": "production", "version": "1.0"}
                )
            }
        }

    def get_config(self, environment: str, agent_type: str) -> AgentConfig:
        """Ottiene configurazione per ambiente e tipo agente"""

        if environment not in self.configs:
            raise ValueError(f"Ambiente {environment} non configurato")

        if agent_type not in self.configs[environment]:
            raise ValueError(f"Agente {agent_type} non configurato per {environment}")

        return self.configs[environment][agent_type]

    def create_agent_from_config(self, environment: str, agent_type: str):
        """Crea agente basato su configurazione"""

        config = self.get_config(environment, agent_type)

        create_params = {
            "name": config.name,
            "instructions": config.instructions,
            "model": config.model,
            "tools": config.tools
        }

        # Aggiunge parametri opzionali se specificati
        if config.temperature != 0.1:  # Solo se diverso dal default
            create_params["temperature"] = config.temperature

        if config.max_tokens:
            create_params["max_tokens"] = config.max_tokens

        if config.metadata:
            create_params["metadata"] = config.metadata

        return client.beta.assistants.create(**create_params)

class DeploymentManager:
    """
    Gestisce il deployment di agenti in produzione
    """

    def __init__(self):
        self.deployed_agents = {}
        self.deployment_history = []

    def deploy_agent(self, agent_id: str, environment: str, agent_type: str, version: str = "1.0"):
        """
        Deploya un agente in un ambiente specifico
        """
        import datetime

        deployment_key = f"{environment}_{agent_type}"

        # Backup dell'agente precedente (se esiste)
        if deployment_key in self.deployed_agents:
            old_deployment = self.deployed_agents[deployment_key]
            print(f"⚠️ Sostituendo agente esistente: {old_deployment['agent_id']}")

        # Nuovo deployment
        deployment_record = {
            "agent_id": agent_id,
            "environment": environment,
            "agent_type": agent_type,
            "version": version,
            "deployed_at": datetime.datetime.now(),
            "status": "active"
        }

        self.deployed_agents[deployment_key] = deployment_record
        self.deployment_history.append(deployment_record.copy())

        print(f"✅ Agente {agent_type} deployato in {environment}")
        return deployment_key

    def rollback_deployment(self, environment: str, agent_type: str):
        """
        Rollback all'ultima versione funzionante.
        Nota: viene usato se la versione corrente non funziona
        """
        deployment_key = f"{environment}_{agent_type}"

        # Trova l'ultima versione precedente
        relevant_history = [
            d for d in self.deployment_history
            if d["environment"] == environment and d["agent_type"] == agent_type
        ]

        if len(relevant_history) < 2:
            print("❌ Nessuna versione precedente per rollback")
            return None

        # Prende la penultima versione
        previous_deployment = relevant_history[-2]

        # Rollback
        rollback_record = previous_deployment.copy()
        rollback_record["deployed_at"] = datetime.datetime.now()
        rollback_record["status"] = "rollback"

        self.deployed_agents[deployment_key] = rollback_record
        self.deployment_history.append(rollback_record)

        print(f"🔄 Rollback completato per {agent_type} in {environment}")
        return rollback_record["agent_id"]

    def get_active_agent(self, environment: str, agent_type: str) -> Optional[str]:
        """Ottiene l'ID dell'agente attivo"""

        deployment_key = f"{environment}_{agent_type}"

        if deployment_key in self.deployed_agents:
            return self.deployed_agents[deployment_key]["agent_id"]

        return None

    def health_check(self, environment: str) -> Dict:
        """Verifica lo stato di salute degli agenti in un ambiente"""

        results = {
            "environment": environment,
            "timestamp": datetime.datetime.now(),
            "agents": {},
            "overall_status": "healthy"
        }

        # Controlla tutti gli agenti nell'ambiente
        for key, deployment in self.deployed_agents.items():
            if deployment["environment"] == environment:
                agent_type = deployment["agent_type"]
                agent_id = deployment["agent_id"]

                try:
                    # Test semplice: recupera info agente
                    agent_info = client.beta.assistants.retrieve(agent_id)

                    results["agents"][agent_type] = {
                        "status": "healthy",
                        "agent_id": agent_id,
                        "last_check": datetime.datetime.now()
                    }

                except Exception as e:
                    results["agents"][agent_type] = {
                        "status": "error",
                        "error": str(e),
                        "agent_id": agent_id
                    }
                    results["overall_status"] = "degraded"

        return results

# Sistema di logging strutturato
class AgentLogger:
    """
    Sistema di logging per agenti in produzione
    """

    def __init__(self, log_level="INFO"):
        import logging

        self.logger = logging.getLogger("AgentSystem")
        self.logger.setLevel(getattr(logging, log_level))

        # Formato log strutturato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_conversation(self, user_id: str, agent_id: str, message: str, response: str, metadata: Dict = None):
        """Log conversazione"""

        log_data = {
            "event": "conversation",
            "user_id": user_id,
            "agent_id": agent_id,
            "message_length": len(message),
            "response_length": len(response),
            "metadata": metadata or {}
        }

        # json.dumps() converte un oggetto Python (come un dizionario) in una stringa JSON formattata
        # Questo è utile per loggare strutture dati complesse in formato leggibile
        self.logger.info(f"Conversation logged: {json.dumps(log_data)}")

    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """Log errore"""

        error_data = {
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }

        self.logger.error(f"Error logged: {json.dumps(error_data)}")

    def log_performance(self, agent_id: str, operation: str, duration: float, success: bool = True):
        """Log performance"""

        perf_data = {
            "event": "performance",
            "agent_id": agent_id,
            "operation": operation,
            "duration_seconds": duration,
            "success": success
        }

        self.logger.info(f"Performance logged: {json.dumps(perf_data)}")

# Esempio di deployment completo
def demo_production_deployment():
    """
    Dimostra un deployment completo in produzione di un agente conversazionale.

    Questa funzione simula l'intero ciclo di vita di un deployment, includendo:
    - Configurazione iniziale e setup dell'ambiente
    - Creazione e deploy di un agente di customer service
    - Monitoraggio dello stato di salute del sistema
    - Gestione degli errori con rollback automatico

    La funzione utilizza:
    - ConfigManager: per gestire le configurazioni dell'agente
    - DeploymentManager: per gestire il deployment e il rollback
    - AgentLogger: per il logging di eventi, performance ed errori

    Returns:
        None. I risultati del deployment vengono stampati a console e loggati.

    Raises:
        Exception: In caso di errori durante il deployment, viene loggato
        l'errore e mostrato un messaggio appropriato.
    """

    # 1. Setup configurazione e deployment
    config_manager = ConfigManager()
    deployment_manager = DeploymentManager()
    logger = AgentLogger()

    print("=== Deployment Pipeline ===")

    # 2. Crea agenti per produzione
    try:
        # Agente customer service
        cs_agent = config_manager.create_agent_from_config("production", "customer_service")

        # Deploy in produzione
        cs_deployment_key = deployment_manager.deploy_agent(
            cs_agent.id,
            "production",
            "customer_service",
            version="2.1"
        )

        logger.log_performance(cs_agent.id, "deployment", 1.2, success=True)

        # 3. Health check
        health_status = deployment_manager.health_check("production")
        print(f"\nHealth Check Result: {health_status['overall_status']}")

        for agent_type, status in health_status["agents"].items():
            print(f"- {agent_type}: {status['status']}")

        # 4. Simulazione errore e rollback
        print(f"\n=== Simulazione Rollback ===")

        # Simula problema con versione corrente
        logger.log_error(
            "agent_malfunction",
            "Agente non risponde correttamente",
            {"agent_id": cs_agent.id, "environment": "production"}
        )

        # Rollback
        rollback_agent_id = deployment_manager.rollback_deployment("production", "customer_service")

        if rollback_agent_id:
            logger.log_performance(rollback_agent_id, "rollback", 0.5, success=True)

        print("✅ Deployment pipeline completata")

    except Exception as e:
        logger.log_error("deployment_failure", str(e))
        print(f"❌ Deployment fallito: {e}")

# Esegui demo deployment
# demo_production_deployment()
```

---

## 10. Conclusioni e Risorse

### Checklist per Progetti Agentic

```python
class ProjectChecklist:
    """
    Checklist per progetti con agenti AI
    """

    def __init__(self):
        self.checklist = {
            "planning": [
                "✓ Definiti use case e obiettivi specifici",
                "✓ Mappati i workflow e i punti di handoff",
                "✓ Identificate le competenze richieste per ogni agente",
                "✓ Stimati volumi di traffico e costi operativi"
            ],

            "development": [
                "✓ Implementati guardrails di sicurezza",
                "✓ Configurato logging e monitoraggio",
                "✓ Scritti test per scenari principali",
                "✓ Documentate le API e integrazioni",
                "✓ Implementata gestione errori robusta"
            ],

            "testing": [
                "✓ Test di stress e performance",
                "✓ Test di sicurezza e edge cases",
                "✓ Validazione accuracy delle risposte",
                "✓ Test dei flussi di handoff",
                "✓ Review delle conversazioni campione"
            ],

            "deployment": [
                "✓ Configurati ambienti dev/staging/prod",
                "✓ Implementato sistema di deployment automatizzato",
                "✓ Configurato monitoraggio in tempo reale",
                "✓ Preparato piano di rollback",
                "✓ Training del team di supporto"
            ],

            "monitoring": [
                "✓ Metriche di performance definite",
                "✓ Alerts configurati per anomalie",
                "✓ Dashboard per stakeholder",
                "✓ Processo di review periodica",
                "✓ Meccanismo di feedback utenti"
            ]
        }

    def print_checklist(self):
        """Stampa la checklist completa"""
        for phase, items in self.checklist.items():
            print(f"\n=== {phase.upper()} ===")
            for item in items:
                print(item)

# Stampa checklist
checklist = ProjectChecklist()
checklist.print_checklist()
```

### Risorse e Next Steps

````markdown
## 📚 Risorse per Approfondimento

### Documentazione Ufficiale

- [OpenAI Assistants API](https://platform.openai.com/docs/assistants)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

### Strumenti Utili

- **Testing**: Postman, Insomnia per API testing
- **Monitoring**: Datadog, New Relic, custom dashboards
- **Security**: OWASP guidelines per AI applications
- **Cost Management**: OpenAI usage tracking, budget alerts

### Community e Support

- OpenAI Developer Community
- GitHub repositories con esempi
- Stack Overflow per troubleshooting

## 🚀 Next Steps Consigliati

1. **Inizia Semplice**: Crea un agente base per familiarizzare
2. **Itera Rapidamente**: Testa, misura, migliora
3. **Scala Gradualmente**: Aggiungi complessità step by step
4. **Monitora Sempre**: Metrics dal giorno 1
5. **Documenta Tutto**: Per team future e maintenance

## ⚡ Quick Start Template

```python
# Template base per nuovo progetto
def quick_start_agent():
    agent = client.beta.assistants.create(
        name="Il Mio Primo Agente",
        instructions="Descrivi qui il comportamento desiderato",
        model="gpt-4-turbo-preview",
        tools=[]  # Aggiungi tools se necessari
    )

    # Crea conversazione
    thread = client.beta.threads.create()

    # Invia messaggio
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Ciao! Come funzioni?"
    )

    # Esegui agente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=agent.id
    )

    # ... gestisci response ...

    return agent, thread
```
````

---

## 🎯 Conclusione

Questa guida ti ha fornito una base solida per lavorare con gli agenti OpenAI:

- **Concetti Base**: Agenti, tools, sessioni
- **Implementazioni Pratiche**: Codice commentato step-by-step
- **Pattern Avanzati**: Handoffs, guardrails, monitoring
- **Produzione**: Deployment, ottimizzazione, best practices

Gli agenti AI rappresentano il futuro dell'automazione intelligente.
Con questa guida hai tutti gli strumenti per iniziare a costruire soluzioni robuste e scalabili.

Ricorda: L'intelligenza artificiale è uno strumento potente, ma il vero valore emerge dall'applicazione thoughtful ai problemi reali. Inizia con casi d'uso concreti, itera velocemente, e scala responsabilmente.

---

## 📋 Appendice: Codice di Riferimento Rapido

### Creazione Agente Base

```python
agent = client.beta.assistants.create(
    name="Nome Agente",
    instructions="Istruzioni comportamento",
    model="gpt-4-turbo-preview"
)

# Crea thread
thread = client.beta.threads.create()

# Aggiungi messaggio
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Messaggio utente"
)

# Esegui agente
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=agent.id
)

# Attendi completamento
while run.status in ["queued", "in_progress"]:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

tool_definition = {
    "type": "function",
    "function": {
        "name": "nome_funzione",
        "description": "Descrizione per l'agente",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Descrizione parametro"
                }
            },
            "required": ["param1"]
        }
    }
}

if run.status == "requires_action":
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Esegui funzione
        result = my_function(**arguments)

        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": json.dumps(result)
        })

    # Invia risultati
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )

def simple_handoff(thread_id, from_agent_id, to_agent_id, context=""):
    # Messaggio di transizione
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content=f"Trasferisco la conversazione. Contesto: {context}"
    )

    # Continua con nuovo agente
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=to_agent_id
    )

    return run

def basic_content_filter(content):
    forbidden_words = ["hack", "bypass", "jailbreak"]

    for word in forbidden_words:
        if word.lower() in content.lower():
            return False, f"Contenuto bloccato: {word}"

    return True, "OK"

# Uso
is_safe, message = basic_content_filter(user_input)
if not is_safe:
    print(f"Bloccato: {message}")

```
