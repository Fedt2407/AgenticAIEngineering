#############################################################
# In questo file viene terstato il laboratorio 3 della week 1
#############################################################

# NOTA: verrà fatta una demo funzionante per il progetto Domus Revita

import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
# gradio è un'interfaccia per dialogare con gli LLM
import gradio as gr

load_dotenv(override=True)

# Carichiamo la variabile ambientale
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
if deepseek_api_key:
    print("DeepSeek API key available")

# Definiamo l'endpoint ed il modello da usare
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
deepseek_model = "deepseek-chat"

# Inizializziamo la classe (usando la classe base di OpenAI)
deepseek = OpenAI(api_key=deepseek_api_key, base_url=DEEPSEEK_BASE_URL)

# Definiamo il lettore di PDF
reader = PdfReader("../1_foundations/me/Domus_Revita_Brief.pdf")

# Estrtaimo il testo dal PDF
presentation_brief = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        presentation_brief += text

# print(presentation_brief)

# Leggiamo il testo me.txt nella stessa cartella del pdf
with open("../1_foundations/me/domus-revita.txt", "r", encoding="utf-8") as file:
    busness_model_description = file.read()

# print(busness_model_description)

# Definiamo il promt di sistema
name = "Domus Revita"

system_prompt = f"Tu stai agendo come {name}. Stai rispondendo a domande sul sito web di {name}, società che offre servizi di riqualificazione imobiliare \
in particolare domande relative alla tipologia di intervento di ruqualificazione immobiliare, alle modalità ed alle tempistiche del servizio fornito da {name}. \
La tua responsabilità è rappresentare {name} nelle interazioni sul sito web nel modo più fedele possibile. \
Ti vengono forniti un riassunto del modello di business di {name} estratto da una presentazione sintetica che puoi utilizzare per rispondere alle domande. \
Sii professionale e coinvolgente, come se stessi parlando con un potenziale cliente per invogliarlo ad approfondire e chidere un contatto ai nostri esperti. \
Se non conosci la risposta, dillo."

# Aggiungiamo info aggiuntive (in un sistema complesso sarebbero potute essere aggiunte in un secondo momento in modo automatico)
system_prompt += f"\n\n## Riassunto:\n{busness_model_description}\n\n## Presentazione sintetica:\n{presentation_brief}\n\n"
system_prompt += f"Con questo contesto, per favore chatta con l'utente, rimanendo sempre nel personaggio di operatore commmerciale di {name}."

# print(system_prompt)


##########################################
# In questa sezione viene definita la chat
##########################################

# # Questa è le definizione iniziale senza il sistema di valutazione
# def chat(message, history):
#     """
#     Gestisce una conversazione con il modello DeepSeek, mantenendo il contesto della chat.

#     Args:
#         message (str): Il messaggio dell'utente da inviare al modello
#         history (list): La cronologia dei messaggi precedenti della conversazione

#     Returns:
#         str: La risposta generata dal modello DeepSeek

#     Note:
#         La funzione combina il prompt di sistema, la cronologia della chat e il nuovo messaggio
#         per mantenere il contesto della conversazione. Utilizza il modello DeepSeek per generare
#         una risposta appropriata basata su tutto il contesto fornito.
#     """

#     messages = [{
#         "role": "system",
#         "content": system_prompt
#     }] + history + [{
#         "role": "user",
#         "content": message
#     }]

#     response = deepseek.chat.completions.create(
#         model=deepseek_model,
#         messages=messages
#     )
    
#     return response.choices[0].message.content

# # Lancia l'interfaccia di gradio NOTA: è necessario specificare il parametro share=True in launch() per visualizzare Gradio sul browser
# gr.ChatInterface(chat, type="messages").launch(share=True)


######################################################################
# In questa sezione viene definito l'LLM che effettuerà la valutazione
######################################################################

# Impostiamo lo schema Pydantic di Python per definire la tipologia di output ammmesso
from pydantic import BaseModel

# La classe Evaluation eredita dalla classe base BaseModel
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

# Definiamo il prompt per la valutazione che verrà utilizzato succesivamente nella funzione evaluate()
evaluator_system_prompt = f"Sei un valutatore che decide se una risposta a una domanda è accettabile. \
Ti viene fornita una conversazione tra un Utente e un Agente. Il tuo compito è decidere se l'ultima risposta dell'Agente è di qualità accettabile. \
L'Agente sta interpretando il ruolo di {name} e sta rappresentando {name} sul loro sito web. \
All'Agente è stato indicato di essere professionale e coinvolgente, come se stesse parlando con un potenziale cliente che ha visitato il sito web. \
All'Agente sono state fornite informazioni su {name} sotto forma di riepilogo e dettagli LinkedIn. Ecco le informazioni:"

evaluator_system_prompt += f"\n\n## Riepilogo:\n{busness_model_description}\n\n## Profilo LinkedIn:\n{presentation_brief}\n\n"
evaluator_system_prompt += f"Con questo contesto, per favore valuta l'ultima risposta, indicando se la risposta è accettabile e fornendo il tuo feedback."

# Genera un prompt strutturato per il valutatore che include la cronologia della chat, l'ultimo messaggio e la risposta da valutare
def evaluator_user_prompt(reply, message, history):
    """Genera il prompt per la valutazione della conversazione tra utente e agente.

    Args:
        reply (str): L'ultima risposta dell'agente da valutare
        message (str): L'ultimo messaggio dell'utente 
        history (list): La cronologia della conversazione precedente

    Returns:
        str: Il prompt completo per il valutatore contenente la conversazione e la richiesta di valutazione

    Note:
        La funzione combina la cronologia della chat, l'ultimo messaggio dell'utente e la risposta dell'agente
        in un unico prompt strutturato per il valutatore. Include anche la richiesta esplicita di valutare
        l'accettabilità della risposta e fornire feedback.
    """
    user_prompt = f"Ecco la conversazione tra l'Utente e l'Agente: \n\n{history}\n\n"
    user_prompt += f"Ecco l'ultimo messaggio dell'Utente: \n\n{message}\n\n"
    user_prompt += f"Ecco l'ultima risposta dell'Agente: \n\n{reply}\n\n"
    user_prompt += "Per favore valuta la risposta, indicando se è accettabile e fornendo il tuo feedback."
    return user_prompt

# Definiamo il modello OpenAI per la valutazione (scegliamo un modello diverso da quello che ha generato la risposta)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=openai_api_key)
openai_model = "gpt-4o-mini"

# Definiamo la funzione di valutazione
# IMPORTANTE con il simbolo -> si indica che ci si aspetta un output di classe Pydantic Evaluation come definita più su
def evaluate(reply, message, history) -> Evaluation:
    """
    Valuta la qualità della risposta fornita dall'agente conversazionale utilizzando il modello OpenAI GPT-4.

    Args:
        reply (str): L'ultima risposta dell'agente da valutare
        message (str): L'ultimo messaggio dell'utente nella conversazione
        history (list): Lo storico completo della conversazione precedente

    Returns:
        Evaluation: Un oggetto contenente:
            - is_acceptable (bool): True se la risposta soddisfa gli standard qualitativi
            - feedback (str): Una valutazione dettagliata che spiega i punti di forza/debolezza

    Note:
        La funzione utilizza il modello gpt-4o-mini di OpenAI per valutare se la risposta:
        - È appropriata al contesto della conversazione
        - Mantiene un tono professionale e coinvolgente
        - Riflette accuratamente le informazioni fornite nel profilo
        - Soddisfa gli standard qualitativi attesi per un'interazione sul sito web
    """

    # Forniamo all'LLM sia le istruzioni (evaluator_system_prompt) che il contesto della conversazione (evaluator_user_prompt)
    # Quest'ultimo continere reply (ultima risposta dell'LLM), message (ultimo messaggio inserito dall'utente) e history (lo storico della conversazione)
    messages = [{
        "role": "system",
        "content": evaluator_system_prompt
    }] + [{
        "role": "user",
        "content": evaluator_user_prompt(reply, message, history)
    }]

    # Il metodo parse() converte automaticamente la risposta JSON nella classe response_format specificata (Evaluation)
    # L'uso di .beta è necessario poiché parse() è una funzionalità beta delle API OpenAI che permette il parsing diretto
    # delle risposte in oggetti Python come la nostra classe Evaluation
    response = openai.beta.chat.completions.parse(
        model=openai_model,
        messages=messages,
        response_format=Evaluation # questo parametro permette di convertire la risposta JSON dell'LLM nel formato richiesto dalla classe Pydantic Evaluate
    )

    return response.choices[0].message.parsed


################################################################################################
# Definiamo un messaggio specifico (possiedi un brevetto?) per testare il sistema di valutazione
################################################################################################

messages = [{
    "role": "system",
    "content": system_prompt
}] + [{
    "role": "user",
    "content": "Possiedi un brevetto?"
}]
response = deepseek.chat.completions.create(
    model=deepseek_model,
    messages=messages
)
reply = response.choices[0].message.content

# Questa funzione permetterà di valutare l'output dell'LLM
# Passiamo solo la risposta dell'LLM, la domanda (hardcoded) e il primo messaggio (messages[:1]) invece dell'intera history
evaluate(reply, "Possiedi un brevetto?", messages[:1])


#############################################################################################################
# Definiamo la funzione per fare in modo che l'LLM dia un'altra risposta se non viene superata la validazione
#############################################################################################################

def rerun(reply, message, history, feedback):
    """
    Genera una nuova risposta dall'LLM quando la precedente non ha superato la validazione.
    Questa funzione aggiorna il prompt di sistema con informazioni sulla risposta rifiutata
    e il relativo feedback, per poi richiedere una nuova risposta all'LLM che tenga conto
    di questi elementi.

    Args:
        reply (str): La risposta precedente che non ha superato la validazione
        message (str): Il messaggio originale dell'utente
        history (list): Lo storico della conversazione
        feedback (str): Il feedback ricevuto sul perché la risposta è stata rifiutata

    Returns:
        str: La nuova risposta generata dall'LLM
    """
    updated_system_prompt = system_prompt + "\n## la precedente risposta è stata rifiutata\nhai tentato di rispondere ma il contollo di qualità ha rifiutato la risposta\n\n"
    updated_system_prompt += f"Il tuo tentativo di risposta: {reply}\n\n"
    updated_system_prompt += f"Il motivo per il rifiuto della risposta: {feedback}\n\n"

    # Definiamo il messaggio per l'LLM che contiene il messaggio di sistema aggiornato, lo storico ed il messaggio dell'utente
    messages = [{
        "role": "system",
        "content": updated_system_prompt
    }] + history + [{
        "role": "user",
        "content": message
    }]
    response = deepseek.chat.completions.create(
        model=deepseek_model,
        messages=messages
    )
    return response.choices[0].message.content

############################################################
# Chat completa che include l'intera pipeline di validazione
############################################################

# NOTA: in questo esempio viene forzato il sistema a fornire una risposta non accettabile in Pig Latin per forzare il sistema di validazione
# NOTA: il Pig Latin è un gioco linguistico nato dall'inglese che sposta le lettere per rendere il linguaggio poco comprensibile

def chat(message, history):

    # Definiamo un caso "speciale" per forzare la funzione di validazione
    if "brevetto" in message:
        system = system_prompt + "\nrispondi generando la risposta in Pig Latin. È essenziale che l'intera risposta sia in Pig Latin"
    else:
        system = system_prompt

    # Generiamo la risposta iniziale dell'LLM
    messages = [{
        "role": "system",
        "content": system
    }] + history + [{
        "role": "user",
        "content": message
    }]
    response = deepseek.chat.completions.create(
        model=deepseek_model,
        messages=messages
    )
    reply = response.choices[0].message.content

    # Utilizziamo la funzione evalute per valutare la risposta (reply)
    # NOTA: la funzione evaluate() restituisce un oggetto Pydantic con i parametri is_acceptable (bool) e feedback (str)
    evaluation = evaluate(reply, message, history)
    # print(f"Questa è la mia valutazione: {evaluation}")

    # Definiamo l'accettabilità della risposta accedendo alla propietà is_acceptable della funzione evaluate()
    if evaluation.is_acceptable:
        print("Valutazione superata, inoltro la risposta")
    else:
        print(f"Valutazione non superata con il seguente feedback\n{evaluation.feedback}")
        # Lanciamo la funzione rerun() fornendo la risposta data precedentemente ed il feedback
        reply = rerun(reply, message, history, evaluation.feedback)
    return reply
    
# Lancia l'interfaccia di gradio NOTA: è necessario specificare il parametro share=True in launch() per visualizzare Gradio sul browser
# NOTA: Gradio prende come argomenti la funzione e type come parametri principali
# NOTA: type="messages" indica che viene forninito il formato openai:
# messages = [{
#         "role": "...",
#         "content": "..."
#     }]
gr.ChatInterface(chat, type="messages").launch(share=True)