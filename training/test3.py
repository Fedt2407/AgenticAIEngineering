#############################################################
# In questo file viene terstato il laboratorio 4 della week 1
#############################################################

from dotenv import load_dotenv
import os
import json
import requests
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)

# Richiamiamo le variabili ambientali di Pushover
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

# Inizializzaimo il modello e veridichiamo le variabili ambientali
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if deepseek_api_key and pushover_user and pushover_token:
    print("All API Keys availble")
else:
    print("Missing API Keys -> Check .env variables")

# Inizializziamo il modello LLM
deepseek_model = "deepseek-chat"
deepseek_url = "https://api.deepseek.com/v1"
deepseek = OpenAI(api_key=deepseek_api_key, base_url=deepseek_url)

# Funzione per madare un messaggio con Pushover
def push(message):
    # creiamo il payload da passare a Pushover
    payload = {
        "user": pushover_user,
        "token": pushover_token,
        "message": message
    }
    # Lanciamo la richiesta passando l'url ed il payload di dati nel formato richiesto
    requests.post(pushover_url, data=payload)

# Facciamo un test per vedere che Pushover funzioni
# push("Questo è un test")


###############################
# Creazione delle funzioni TOOL
###############################

# Questa funzione è usata per salvare le informazioni di un nuovo utente
def record_user_details(name, email="Email non fornita", notes="Note non fornite"):
    push(f"Ho salvato le informazioni dell'utente: {name}, con email: {email} e le seguenti note: {notes}")
    return {"recorded": "ok"}

# Questa funzione è utilizzata per salvare le domande a cui il sistema non è in grado di rispondere
def record_unknown_question(question):
    push(f"Ho salvato la seguente domanda a cui non so rispondere:\n{question}")
    return {"recorded": "ok"}


#########################################
# Creazione delle strutture JSON dei TOOL
#########################################

# IMPORTANTE: una volta forniti i TOOL all'LLM sarà lui a decidere quando e se utilizzarli

# NOTA: Questa parte di codice serve unicamente per comprendere la struttura del JSON
# NOTA: In un contesto reale useremo di decoratore @function_tool che trasforma automaticamente un funzione in un JSON schema

record_user_details_json = {
    "name": "record_user_details",
    "description": "Usa questo tool per registrare che l'utente è disponibile ad essere ricontattato avendo fornito email ed eventuali note",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "L'email fornita dall'utente"
            },
            "name": {
                "type": "string",
                "description": "Il nome fornito dall'utente (opzionale)"
            },
            "notes": {
                "type": "string",
                "description": "Le note fornite dall'utente (opzionale)"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Usa questo tool per registrare la domanda a cui il sistema non è riuscito a rispondere",
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "La domanda a cui non è stato possibile dare una risposta"
        },
        "required": ["question"],
        "additionalProperties": False
    }

}

# definiamo di seguito la lista dei tool disponibili
tools = [
    {
        "type": "function",
        "function": record_user_details_json
    },
    {
        "type": "function",
        "function": record_unknown_question_json
    }
]

# Facciamo una prova per controllare dal terminal che i tool siano pronti per essere usati nell'LLM
# for tool in tools:
#     print(tool)


############################################################
# Funzione per gestire l'utilizzo dei tool da parte dell'LLM
############################################################

# NOTA: Questa funzione è a scopo di insegnamento 
# La logica condizione in contesti reali dove ci potrebbero essere numerosi tool viene effetuata in modo automatizzato usando globals()

# Questa funzione itera all'interno della lista dei TOOL e decide quale utilizzare sulla base del contesto
def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        # json.loads converte la stringa JSON degli argomenti in un dizionario Python
        # tool_call.function.arguments contiene gli argomenti della funzione come stringa JSON
        arguments = json.loads(tool_call.function.arguments)
        # flush=True forza lo svuotamento del buffer di stampa, assicurando che il messaggio venga mostrato immediatamente
        print(f"Tool chiamato: {tool_name}", flush=True)

    # IF STATEMENT - È la rappresentazione di quello che fa la funzione globals() usata di seguito
    # if tool_name == "record_user_details":
    #     result = record_user_details(**arguments)
    # elif tool_name == "record_unknown_question":
    #     result = record_unknown_question(**arguments)
    
    # globals() restituisce un dizionario di tutte le variabili globali, incluse le funzioni
    # Usiamo .get(tool_name) per ottenere la funzione corrispondente al nome dello strumento
    tool = globals().get(tool_name)
    # Se la funzione esiste (tool non è None), la chiamiamo con gli argomenti forniti
    # altrimenti restituiamo un dizionario vuoto come fallback
    result = tool(**arguments) if tool else {}

    results.append(
        {
            "role": "tool",
            "content": json.dumps(result),  # Converte il dizionario Python in una stringa JSON (fa l'azione opposta di json.loads)
            "tool_call_id": tool_call.id    # tool_call.id è un attributo fornito dall'oggetto tool_call restituito dall'LLM per identificare univocamente la chiamata
        }
    )

    return results


####################################################################
# Lettura dei documenti PDF / tedsto, preparazione del prompt e chat
####################################################################

reader = PdfReader("../1_foundations/me/linkedin.pdf")
linkedin_pdf_text = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin_pdf_text += text

with open("../1_foundations/me/summary.txt", "r", encoding="utf-8") as file:
    personal_summary = file.read()

name = "Federico Tognetti"

# Definizione del prompt di sistema
system_prompt = f"Tu stai agendo come {name}. Stai rispondendo a domande sul sito web di {name}, \
in particolare domande relative alla carriera, background, competenze ed esperienza di {name}. \
La tua responsabilità è rappresentare {name} nelle interazioni sul sito web nel modo più fedele possibile. \
Ti vengono forniti un riassunto del background di {name} e il suo profilo LinkedIn che puoi utilizzare per rispondere alle domande. \
Sii professionale e coinvolgente, come se stessi parlando con un potenziale cliente o futuro datore di lavoro che ha visitato il sito web. \
Se non conosci la risposta a qualsiasi domanda, usa il tuo strumento record_unknown_question per registrare la domanda a cui non hai potuto rispondere, anche se riguarda qualcosa di banale o non correlato alla carriera. \
Se l'utente è impegnato nella discussione, cerca di indirizzarlo verso un contatto via email; chiedi la sua email e registrala usando il tuo strumento record_user_details."

system_prompt += f"\n\n## Riassunto:\n{personal_summary}\n\n## Profilo LinkedIn:\n{linkedin_pdf_text}\n\n"
system_prompt += f"Con questo contesto, per favore chatta con l'utente, rimanendo sempre nel personaggio di {name}."


# Definizione della chat
# NOTA: verrà usato un while loop
def chat(message, history):
    """
    Gestisce una conversazione con il modello DeepSeek, supportando l'uso di strumenti (tools).

    La funzione implementa un ciclo di conversazione che:
    1. Inizializza i messaggi con il prompt di sistema e la cronologia precedente
    2. Invia i messaggi al modello DeepSeek
    3. Gestisce le chiamate agli strumenti quando richieste dal modello
    4. Continua il ciclo finché non viene generata una risposta finale

    Args:
        message (str): Il messaggio dell'utente da processare
        history (list): La cronologia dei messaggi precedenti nella conversazione

    Returns:
        str: Il contenuto della risposta finale generata dal modello

    Note:
        - Utilizza variabili globali: system_prompt, deepseek, deepseek_model, tools
        - Gli strumenti (tools) devono essere definiti precedentemente
        - Il ciclo continua finché il modello non genera una risposta finale (finish_reason != "tool_call")
    """
    messages = [{
        "role": "system",
        "content": system_prompt
    }] + history + [{
        "role": "user",
        "content": message
    }]

    done = False

    while not done:
        response = deepseek.chat.completions.create(
            model=deepseek_model,
            messages=messages,
            tools=tools # viene aggiuntla la lista dei tools già definiti come sopra
        )

        # Ottiene il motivo di terminazione della risposta dell'LLM (può essere 'stop' per completamento normale,
        # 'length' se ha raggiunto il limite di token, 'tool_calls' se richiede l'uso di uno strumento, etc)
        finish_reason = response.choices[0].finish_reason

        # Se il modello richiede l'uso di uno strumento (tool)
        if finish_reason == "tool_call":
            # Estrae il messaggio dalla risposta del modello
            message = response.choices[0].message
            # Ottiene le specifiche chiamate agli strumenti richieste
            tool_call = message.tool_calls
            # Esegue le chiamate agli strumenti e ottiene i risultati
            results = handle_tool_calls(tool_call)
            # Aggiunge il messaggio originale alla cronologia
            messages.append(message)
            # Aggiunge i risultati delle chiamate agli strumenti alla cronologia
            messages.extend(results)
        else:
            done = True
    
    return response.choices[0].message.content

# Lanciamo Gradio per chattare con l'LLM
gr.ChatInterface(chat, type="messages").launch(share=True)