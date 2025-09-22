############################################################
# In questo file viene testato il laboratorio 3 della week 2
############################################################

# Utilizzo di modelli diversi da OpenAI e Guardrails per controllare gli input e gli output

import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from pydantic import BaseModel
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

# Carichiamo le variabili di sistema
load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if openai_api_key:
    print(f"Openai API Key exists and starts with {openai_api_key[:8]}")
else:
    print("Openai API key not set")

if google_api_key:
    print(f"Google API Key is set and starts with {google_api_key[:8]}")
else:
    print("Google API key not set")

if deepseek_api_key:
    print(f"Deepseek API Key is set and starts with {deepseek_api_key[:8]}")
else:
    print("Deepseek API key not set")

if groq_api_key:
    print(f"Groq API Key is set and starts with {groq_api_key[:8]}")
else:
    print("Groq API key not set")

# Definiamo le istruzioni
instructions1 = """Sei un agente di vendita che lavora per Domus Revita,
un'azienda specializzata in progetti di riqualificazione immobiliare che trasforma vecchie case grandi in due o tre unità abitative rinnovate.
Questa mail è rivolta ai proprietari di grandi case vecchie in zone centrali o di pregio della città.
Il proprietario probabilmente sta faticando a vendere la casa così com'è poiché non è in buone condizioni e servono molti soldi per riqualificarla.
Devi spiegare che il nostro team ha architetti e imprese molto qualificati che possono aiutare a riqualificare la casa.
La vecchia casa grande sarà suddivisa in due unità abitative e completamente ristrutturata.
Una sarà venduta dal nostro team e una rimarrà come pagamento al proprietario che avrà una nuova casa riqualificata da vendere, affittare o abitare.
IMPORTANTE: genera la pubblicità in italiano usando massimo 200 parole.
Scrivi email commerciali professionali e serie."""

instructions2 = """Sei un agente di vendita simpatico, divertente e coinvolgente che lavora per Domus Revita,
un'azienda specializzata in progetti di riqualificazione immobiliare che trasforma vecchie case grandi in due o tre unità abitative rinnovate.
Questa mail è rivolta ai proprietari di grandi case vecchie in zone centrali o di pregio della città.
Il proprietario probabilmente sta faticando a vendere la casa così com'è poiché non è in buone condizioni e servono molti soldi per riqualificarla.
Devi spiegare che il nostro team ha architetti e imprese molto qualificati che possono aiutare a riqualificare la casa.
La vecchia casa grande sarà suddivisa in due unità abitative e completamente ristrutturata.
Una sarà venduta dal nostro team e una rimarrà come pagamento al proprietario che avrà una nuova casa riqualificata da vendere, affittare o abitare.
IMPORTANTE: genera la pubblicità in italiano usando massimo 200 parole.
Scrivi email commerciali spiritose e coinvolgenti che hanno buone probabilità di ottenere una risposta."""

instructions3 = """Sei un agente di vendita impegnato e con poco tempo a disposizione che lavora per Domus Revita,
un'azienda specializzata in progetti di riqualificazione immobiliare che trasforma vecchie case grandi in due o tre unità abitative rinnovate.
Questa mail è rivolta ai proprietari di grandi case vecchie in zone centrali o di pregio della città.
Il proprietario probabilmente sta faticando a vendere la casa così com'è poiché non è in buone condizioni e servono molti soldi per riqualificarla.
Devi spiegare che il nostro team ha architetti e imprese molto qualificati che possono aiutare a riqualificare la casa.
La vecchia casa grande sarà suddivisa in due unità abitative e completamente ristrutturata.
Una sarà venduta dal nostro team e una rimarrà come pagamento al proprietario che avrà una nuova casa riqualificata da vendere, affittare o abitare.
IMPORTANTE: genera la pubblicità in italiano usando massimo 200 parole.
Scrivi email commerciali concise e dirette al punto."""

# Definiamo gli endpoint poe i modelli non OpenAI (al monto le uniche chiavi API oltre ad OpenAI sono quelle di DeepSeek)
# GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
# GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Effettuamo l'inizializzazione delle classi per tutti gli agenti LLM
# Inizializziamo i client usando AsyncOpenAI invece del normale OpenAI perché:
# 1. Questi servizi (Gemini, Deepseek, Groq) espongono API compatibili con OpenAI
# 2. AsyncOpenAI permette di fare chiamate asincrone, migliorando le performance
# 3. Possiamo specificare base_url diversi per ogni servizio mantenendo la stessa interfaccia
# Creiamo i client per ogni servizio, specificando l'endpoint e la chiave API
# gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key) # Chiave non disponibile
deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
# groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key) # Chiave non disponibile

# Usiamo OpenAIChatCompletionsModel invece di OpenAI direttamente perché:
# 1. Questa classe è un wrapper che standardizza l'interfaccia per le chat completions
# 2. Ci permette di usare lo stesso codice per provider diversi
# 3. Gestisce internamente le differenze tra i vari servizi mantenendo la compatibilità
# 4. Possiamo passare il client asincrono creato sopra come parametro
# Creiamo i modelli passando il nome del modello specifico e il client corrispondente
# gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client) # Chiave non disponibile
deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)
# llama3_3_model = OpenAIChatCompletionsModel(model="llama-3.3-70b-versatile", openai_client=groq_client) # Chiave non disponibile

# Inizializziamo i tre agenti di vendita
# IMPORTANTE: se passiamo un testo es. "gpt-4-mini" la classe assume che ci si connetta direttamente all'LLM di OpenAI 
# se invece viene passato un oggetto relativo all'istanza di un modello la classe si connetterà a quello specifico modello
sales_agent1 = Agent(
    name="Deepseek sales agent 1",
    instructions=instructions1,
    model=deepseek_model
)

sales_agent2 = Agent(
    name="Deepseek sales agent 2",
    instructions=instructions2,
    model=deepseek_model
)

sales_agent3 = Agent(
    name="OpenAI sales agent",
    instructions=instructions3,
    model="gpt-4o-mini"
)

# Trasformiamo i tre agenti di vendita in tool con il metodo .as_tool
description = "Scrivi una mail di vendita a freddo"

tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1",
    tool_description=description
)

tool2 = sales_agent2.as_tool(
    tool_name="sales_agent2",
    tool_description=description
)

tool3 = sales_agent3.as_tool(
    tool_name="sales_agent3",
    tool_description=description
)

# Creiamo adesso i tool per l'invio della mial
# Creiamo un tool a partire da una funzione con il decoratore @function_tool
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Invia una mail di vendita a freddo con uno specifico oggetto ed un corpo in html a prospect
    """
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("federico.tognetti@gmail.com")
    to_email = To("federico.tognetti@gmail.com")
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

# Creiamo adesso altri due tool partendo dagli agenti
# TOOL 1
subject_instructions = (
    "Sei un copywriter esperto nello scrivere l'oggetto per una email di vendita a freddo."
    "Ti viene fornito un messaggio e devi scrivere un oggetto per una email che ha buone probabilità di essere aperta ottenere una risposta."
)

subject_writer = Agent(
    name="Subject writer",
    instructions=subject_instructions,
    model="gpt-4o-mini"
)

subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Scrivi l'oggetto per una mail di vendita a freddo"
)

# TOOL 2
html_instructions = (
    "Sei un esperto nel convertire il corpo di una email testuale in un corpo email HTML."
    "Ti viene fornito il corpo di una email testuale che potrebbe contenere dei markdown"
    "Devi convertirlo in un corpo email HTML con un layout e un design elaborato, chiaro e convincente."
)

html_converter = Agent(
    name="HTML composer",
    instructions=html_instructions,
    model="gpt-4o-mini"
)

html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Sei un esperto a trasformare il corpo di una mail da testo a HTML"
)
    
# Facciamo la lista dei tool per la gestione della mail
email_tools = [subject_tool, html_tool, send_html_email]

# Creaimo l'handoff che si occuperà di crearte l'oggetto e convertire il corpo del testo e spedire la mail
instructions = (
    "Sei esperto nel creare l'oggetto, formattare il corpo e spedire le email. Ricevi il corpo di una email da inviare."
    "Prima utilizzi il tool subject_writer per scrivere l'oggetto dell'email, poi utilizzi il tool html_converter per convertire il corpo in HTML."
    "Infine, utilizzi il tool send_html_email per inviare l'email con l'oggetto e il corpo HTML."
    "IMPORTANTE: Una volta completato l'invio dell'email, termina il processo. Non richiedere ulteriori handoff."
)

emailer_agent = Agent(
    name="Emailer agent",
    instructions=instructions,
    model="gpt-4o-mini",
    tools=email_tools,
    handoff_description="Genera l'oggetto, converti la mail e spediscila"
)

# Prepariamo l'agente principale Sales Manager principale a cui andranno associati i tool e handoff
tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]

# Definiamo le istruzioni per l'LLM
sales_manager_instructions = """
Sei un Sales Manager di Domus Revita. Il tuo obiettivo è trovare la migliore email di vendita a freddo utilizzando i tools sales_agent.

Segui attentamente questi passaggi:
1. Genera le Bozze: Utilizza tutti e tre i tools sales_agent per generare tre diverse bozze di email. Non procedere finché non hai tutte e tre le bozze pronte.

2. Valuta e Seleziona: Esamina le bozze e scegli la singola email migliore basandoti sul tuo giudizio di quale sia la più efficace.
Puoi utilizzare i tools massimo 2 volte se non sei soddisfatto dei risultati del primo tentativo.

3. Passaggio per l'Invio: Passa SOLO la bozza vincente all'agente 'Emailer agent'. L'Emailer agent si occuperà della formattazione e dell'invio.

Regole Fondamentali:
- Devi utilizzare i tools sales agent massimo 2 volte per generare le bozze — non scrivere le bozze tu stesso e mantieni la lingua italiana.
- Devi passare esattamente 1 email all'Emailer agent — mai più di una.
- Una volta passato il controllo all'Emailer agent, NON richiamarlo nuovamente.
"""

# Definiamo la funzione per lesecuzione
async def send_dom_rev_formatted_mail():
    """
    Invia mail di vendita dopo aver scelto la miglior formulazione del testo.
    La funzione è provvista di un handoff in grado:
    - di definire l'oggetto sulla base del testo,
    - convertire il corpo del testo in HTML
    - inviare la mail usando Sendgrid
    """

    sales_manager = Agent(
        name="Sales manager",
        instructions=sales_manager_instructions,
        model="gpt-4o-mini",
        tools=tools,
        handoffs=handoffs
    )

    message = "Scrivi ed invia una mail di vendita a freddo per un potenziale cliente che vuole riqualificare la sua casa"

    with trace("Mail formattata Domus Revita"):
        result = await Runner.run(sales_manager, message)
        print(result.final_output)

# asyncio.run(send_dom_rev_formatted_mail()) # Decommenta per eseguire


################################################################################################
# Guardrails - Sono a loro volta agenti che servono principalemente a controllare input e output
################################################################################################

# IMPORTANTE: ci sono diversi tipi di agente ma i principali servono a controllare:
# - Gli input che vengono passati al primo agente del workflow
# - Gli output che sono generati dall'ultimo agente del workflow prima di passare l'output all'utente

# Creazione del Guardrail
# Estenderemo la classe Pydantic BaseModel per definire la struttura dell'output atteso.
# Questo modello ci permette di:
# - Validare automaticamente i dati in ingresso
# - Avere un'interfaccia tipizzata e documentata
# - Garantire la consistenza del formato dei dati
# NOTA: l'ipotesi alla base è che noi non vogliamo ci siano nomi propri di persona all'interno della richiesta da parte dell'utente
class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str

# NOTA: il parameto output_type forza l'agente a non fornire un output testuale come da impostazione di default
# Grazie a questo parametro la struttura dell'output è un oggetto di python che rispetta lo schema definito nella classe Pydantic
guardrail_agent = Agent(
    name="Controllo del nome",
    instructions="Controlla che nessun nome proprio di persona sia inserito nella richiesta da parte dell'utente",
    model="gpt-4o-mini",
    output_type=NameCheckOutput # Definisce la struttura dell'output es. {"is_name_in_message": True, "name": "Serena"} oppure {"is_name_in_message": False, "name": None}
)

# NOTA
# Potremmo usare una classe pydantic per definire meglio la struttura della mail attesa così come ogni output richiesto all'LLM es:
class EmailFormat(BaseModel):
    recipient: str
    subject: str
    body: str
    ...

# Definiamo il Guardrail partendo dall'agente appena creato usando il decoratore @input_guardrail
# NOTA: il principio è similare a quello di creare un agente e trasformarlo in tool con il metodo .as_tool
@input_guardrail
async def guardrail_against_name(ctx, agent, message):
    """
    Un guardrail asincrono che controlla la presenza di nomi propri di persona nel messaggio dell'utente.
    Questa funzione agisce come un controllo di sicurezza per verificare che nessun nome proprio 
    di persona sia presente nel messaggio in input. Utilizza un agente LLM specializzato per 
    effettuare questo controllo.

    Args:
        ctx: Il contesto dell'esecuzione del guardrail
        agent: L'agente che verrà utilizzato dopo il guardrail se il controllo passa
        message (str): Il messaggio dell'utente da controllare

    Returns:
        GuardrailFunctionOutput: Un oggetto contenente:
            - output_info: Un dizionario con il nome trovato (se presente)
            - tripwire_triggered: Un booleano che indica se è stato trovato un nome (True) o no (False)

    Note:
        Il guardrail utilizza un modello GPT per analizzare il testo e identificare nomi propri.
        Se viene trovato un nome, il guardrail viene "attivato" (tripwire_triggered=True) 
        bloccando l'esecuzione del workflow.
    """
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(
        output_info={"found_name": result.final_output.name},
        tripwire_triggered=is_name_in_message
    )


# Creaiamo adesso un agente pià accurato che utilizza anche il guardrail appena definito
async def send_formatted_mail_with_guardrail():
    careful_sales_manager = Agent(
        name="Careful sales manager",
        instructions=sales_manager_instructions,
        model="gpt-4o-mini",
        tools=tools,
        handoffs=handoffs,
        input_guardrails=[guardrail_against_name]
    )

    # NOTA: questo messaggio di input da parte dell'utente attiverrà il guardrail e bloccherà il processo producendo un errore nel terminale
    # message = "Manda una mail di vendita a freddo al potenziale cliente da parte di Alice"

    # NOTA: questo messaggio di input supererà il guardrail con una prosecuzione del processo
    message = "Manda una mail di vendita a freddo al potenziale cliente da del Responsabile Commerciale"

    with trace("Mail formattata con guardrail"):
        result = await Runner.run(careful_sales_manager, message)
        print(result.final_output)

asyncio.run(send_formatted_mail_with_guardrail())

####################################################################
# Funzione generale per l'esecuzione del codice dell'utlima funzione
# IMPORTANTE: con il seguente codice il corpo della mail arriva completamente nero

# async def main():
#     try:
#         print("Processo di generazione mail avviato")
#         result = await send_formatted_mail_with_guardrail()
#         return result
#     except Exception as e:
#         print(f"Errore nell'esecuzione: {e}")
#         return None

# if __name__ == "__main__":
#     asyncio.run(main())