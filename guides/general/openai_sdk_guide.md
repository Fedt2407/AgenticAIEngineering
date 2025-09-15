# Guida agli SDK OpenAI per Agentic AI

## Introduzione

Gli SDK (Software Development Kit) di OpenAI permettono di costruire agenti intelligenti che possono utilizzare strumenti, chiamare funzioni e mantenere conversazioni complesse. Questa guida copre i concetti essenziali per iniziare con l'agentic AI.

## 1. Setup Iniziale

### Installazione

```bash
# Python
pip install openai

# Node.js
npm install openai
```

### Configurazione Base

```python
import openai
from openai import OpenAI

# Inizializza il client con la tua API key
client = OpenAI(
    api_key="sk-your-api-key-here"  # Sostituisci con la tua chiave API
)

# Alternativa: usa variabile d'ambiente OPENAI_API_KEY
# client = OpenAI()  # Legge automaticamente da OPENAI_API_KEY

# NOTA: è possibile usare alrtri LLM come DeepSeek, Anthropic, Gemini, Ollama, ecc.
```

## 2. Chat Completions Base

```python
def basic_chat_example():
    # Crea una conversazione base con il modello
    response = client.chat.completions.create(
        model="gpt-4",  # Specifica il modello da utilizzare
        messages=[
            {
                "role": "system",     # Messaggio di sistema per definire comportamento
                "content": "Sei un assistente esperto in programmazione."
            },
            {
                "role": "user",       # Messaggio dell'utente
                "content": "Spiegami cos'è una funzione ricorsiva"
            }
        ],
        temperature=0.7,  # Controlla la creatività (0.0-2.0)
        max_tokens=500    # Limita la lunghezza della risposta
    )

    # Estrae il contenuto della risposta
    answer = response.choices[0].message.content
    print(f"Risposta: {answer}")

    return answer
```

## 3. Function Calling - Il Cuore dell'Agentic AI

Il function calling permette al modello di chiamare funzioni esterne per ottenere informazioni o eseguire azioni.

### Definizione di Funzioni

```python
import json
from datetime import datetime

# Definisce una funzione di esempio per simulare una chiamata API meteo
def get_current_weather(location, unit="celsius"):
    """Simula l'ottenimento di informazioni meteo."""
    # In un caso reale, qui faresti una chiamata API a un servizio meteo
    weather_data = {
        "location": location,
        "temperature": "22",
        "unit": unit,
        "description": "Soleggiato"
    }
    return json.dumps(weather_data) # json.dumps converte il dizionario Python in una stringa JSON per l'API

def get_current_time():
    """Restituisce l'ora attuale."""
    return datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

# Schema delle funzioni per OpenAI (definisce come il modello può chiamarle)
# È lo schema dei tool che possono essere usati dall'agente
functions = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",        # Nome della funzione
            "description": "Ottieni informazioni meteo per una località",  # Descrizione per il modello
            "parameters": {                       # Parametri accettati
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "La città di cui vuoi il meteo, es. Milano, IT"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],  # Valori ammessi
                        "description": "L'unità di temperatura"
                    }
                },
                "required": ["location"]          # Parametri obbligatori
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Ottieni l'ora e data attuali",
            "parameters": {"type": "object", "properties": {}}  # Nessun parametro
        }
    }
]
```

### Utilizzo delle Funzioni

```python
def agent_with_functions():
    # Dizionario che mappa nomi funzioni alle funzioni Python
    available_functions = {
        "get_current_weather": get_current_weather,
        "get_current_time": get_current_time
    }

    # Messaggio dell'utente
    user_message = "Che tempo fa a Milano e che ore sono?"

    messages = [
        {"role": "system", "content": "Sei un assistente utile con accesso a funzioni."},
        {"role": "user", "content": user_message}
    ]

    # Prima chiamata: il modello decide quali funzioni chiamare
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=functions,              # Passa le funzioni disponibili
        tool_choice="auto"            # Lascia che il modello scelga se/quando usare le funzioni
    )

    # Analizza la risposta
    response_message = response.choices[0].message
    messages.append(response_message)  # Aggiungi la risposta ai messaggi

    # Verifica se il modello vuole chiamare delle funzioni
    if response_message.tool_calls:
        print(f"Il modello vuole chiamare {len(response_message.tool_calls)} funzioni")

        # Esegui ogni funzione richiesta
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name        # Nome della funzione (es. "get_current_weather" o "get_current_time")
            function_args = json.loads(tool_call.function.arguments)  # Argomenti (es. {"location": "Milano"} per get_current_weather o {} per get_current_time)

            print(f"Chiamando {function_name} con argomenti: {function_args}")

            # Chiama la funzione Python corrispondente
            # Verifica se la funzione esiste nel dizionario available_functions
            # Se esiste, la chiama passando gli argomenti ricevuti dal modello
            # **function_args è l'operatore di "unpacking" del dizionario:
            # Se function_args = {"location": "Milano"},
            # available_functions[function_name](**function_args) equivale a:
            # available_functions[function_name](location="Milano")
            if function_name in available_functions:
                function_response = available_functions[function_name](**function_args)

                # Aggiungi il risultato della funzione alla conversazione
                messages.append({
                    "tool_call_id": tool_call.id,    # ID univoco della chiamata
                    "role": "tool",                   # Ruolo: risultato di uno strumento
                    "name": function_name,            # Nome della funzione
                    "content": function_response      # Risultato della funzione
                })

        # Seconda chiamata: il modello elabora i risultati delle funzioni
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages  # Include ora anche i risultati delle funzioni
        )

        # Il risultato ritoranto dalla funzione include adesso la risposta finale dopo aver chiamato i tool
        return final_response.choices[0].message.content

    else:
        # Il modello non ha chiamato i tool, restituisci la risposta diretta
        return response_message.content
```

## 4. Gestione dello Stato della Conversazione

```python
class AIAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [
            {"role": "system", "content": "Sei un assistente AI con memoria della conversazione."}
        ]
        # Riferimento alle funzioni (tools) definite precedentemente nel codice
        # Queste funzioni vengono passate al modello come "functions" per permettergli
        # di sapere quali strumenti ha a disposizione e come utilizzarli
        self.functions = functions
        # Dizionario che mappa i nomi delle funzioni alle loro implementazioni Python
        # Viene usato per eseguire effettivamente le funzioni quando richiesto dal modello
        self.available_functions = {
            "get_current_weather": get_current_weather,
            "get_current_time": get_current_time
        }

    def add_message(self, role, content):
        """Aggiunge un messaggio alla cronologia della conversazione."""
        self.messages.append({"role": role, "content": content})

    def chat(self, user_input):
        """Gestisce una singola interazione con l'utente."""
        # Aggiungi il messaggio dell'utente
        self.add_message("user", user_input) # nella funzione definita sopra "role" è hardcoded in quanto ci si riferisce sempre ad un messaggio dell'utente

        try:
            # Chiama il modello
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.messages,
                tools=self.functions,
                tool_choice="auto" # lascia al modello la libertà di definire quale tool utilizzare
            )

            response_message = response.choices[0].message

            # Aggiungi la risposta del modello alla cronologia
            self.messages.append({
                "role": "assistant", # anche in questo caso il role è hardcoded perché ci si rifersce semopre all'assistente LLM
                "content": response_message.content,
                "tool_calls": response_message.tool_calls
            })

            # Gestisci le chiamate alle funzioni se presenti
            # tool_calls è un attributo del response_message che contiene la lista di tool/funzioni
            # che il modello ha deciso di chiamare. Viene popolato quando il modello decide
            # di utilizzare uno dei tools definiti in self.functions
            # Se tool_calls è presente, significa che il modello vuole eseguire delle funzioni
            if response_message.tool_calls:
                return self._handle_function_calls(response_message.tool_calls) # Usa la funzione privata _handle_function_calls per gestire l'esecuzione dei tools
            else:
                # Se non ci sono tool da chiamare, restituisci direttamente il contenuto della risposta
                return response_message.content

        except Exception as e:
            return f"Errore durante la chiamata API: {str(e)}"

    def _handle_function_calls(self, tool_calls):
        """Gestisce l'esecuzione delle funzioni chiamate dal modello."""
        # Esegui tutte le funzioni richieste
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments) # converte gli argomenti della funzione da stringa JSON in un dizionario Python

            if function_name in self.available_functions:
                # Esegui la funzione
                # L'operatore ** espande il dizionario function_args in coppie chiave-valore da passare come parametri nominali.
                # Ad esempio, se function_args = {"location": "Milano", "unit": "celsius"},
                # l'espansione equivale a chiamare: self.available_functions[function_name](location="Milano", unit="celsius")
                function_result = self.available_functions[function_name](**function_args)

                # Aggiungi il risultato alla conversazione
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_result
                })

        # Ottieni la risposta finale dopo l'esecuzione delle funzioni
        final_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.messages
        )

        final_content = final_response.choices[0].message.content
        self.add_message("assistant", final_content)

        return final_content

    # È un metodo della classe per fornire lo storico della conversazione\
    def get_conversation_history(self):
        """Restituisce la cronologia della conversazione."""
        return self.messages.copy()
```

## 5. Esempio Pratico d'Uso

```python
def main():
    # Crea un'istanza dell'agente
    agent = AIAgent()

    print("Agente AI avviato! (scrivi 'quit' per uscire)")

    while True:
        # Ricevi input dall'utente
        user_input = input("\nTu: ")

        if user_input.lower() == 'quit':
            break

        # Ottieni la risposta dell'agente
        response = agent.chat(user_input)
        print(f"Agente: {response}")

# Esempio di utilizzo
if __name__ == "__main__":
    # main()  # Decommenta per usare l'interfaccia interattiva

    # Oppure testa direttamente:
    agent = AIAgent()

    # Prima interazione
    response1 = agent.chat("Ciao! Che ore sono?")
    print(f"Risposta 1: {response1}")

    # Seconda interazione (l'agente ricorda la conversazione precedente)
    response2 = agent.chat("E che tempo fa a Roma?")
    print(f"Risposta 2: {response2}")

    # Mostra la cronologia completa
    print("\nCronologia conversazione:")
    for msg in agent.get_conversation_history():
        print(f"{msg['role']}: {msg.get('content', '[function_call]')}")
```

## 6. Best Practices

### Gestione degli Errori

```python
def safe_function_call(func, **kwargs):
    """
    Wrapper per eseguire chiamate sicure alle funzioni gestendo le eccezioni.

    Args:
        func: La funzione da eseguire in modo sicuro
        **kwargs: Gli argomenti da passare alla funzione

    Returns:
        dict: Un dizionario contenente:
            - success (bool): True se l'esecuzione ha avuto successo, False altrimenti
            - data: Il risultato della funzione in caso di successo
            - error (str): Il messaggio di errore in caso di fallimento
    """
    try:
        result = func(**kwargs)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Uso nella gestione delle funzioni
function_result = safe_function_call(available_functions[function_name], **function_args)
if function_result["success"]:
    content = function_result["data"]
else:
    content = f"Errore nell'esecuzione di {function_name}: {function_result['error']}"
```

### Limitazione dei Token

```python
def manage_conversation_length(messages, max_tokens=4000):
    """
    Gestisce la lunghezza della conversazione mantenendola entro un limite di token specificato.

    Args:
        messages: Lista di messaggi della conversazione
        max_tokens: Numero massimo di token consentiti (default 4000,  approssimativamente 16.000 caratteri -> 4 caratteri, 1 token)

    Returns:
        Lista di messaggi potenzialmente ridotta per rispettare il limite di token.
        Il messaggio di sistema viene sempre preservato.

    Note:
        Usa un'approssimazione di 4 caratteri per token per la stima.
        Rimuove i messaggi più vecchi quando necessario, preservando sempre il messaggio di sistema.
    """
    # Calcola approssimativamente i token (4 caratteri ≈ 1 token)
    total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)

    # Se supera il limite, rimuovi i messaggi più vecchi (eccetto il sistema)
    while total_chars > max_tokens * 4 and len(messages) > 2:
        if messages[1]['role'] != 'system':  # Non rimuovere mai il messaggio di sistema
            messages.pop(1) # elimina il secondo messaggio dalla lista
        total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)

    return messages
```

## Conclusione

Questa guida copre i concetti essenziali per costruire agenti AI con gli SDK di OpenAI:

1. **Setup base**: Configurazione del client e autenticazione
2. **Chat completions**: Conversazioni semplici
3. **Function calling**: Integrazione con strumenti esterni (tools)
4. **Gestione stato**: Mantenimento della memoria conversazionale
5. **Best practices**: Gestione errori e ottimizzazioni

L'agentic AI si basa sulla capacità del modello di decidere autonomamente quando e come utilizzare gli strumenti a disposizione, creando un comportamento più simile a quello umano nella risoluzione di problemi complessi.
