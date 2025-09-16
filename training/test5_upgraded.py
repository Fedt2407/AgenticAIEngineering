############################################################
# Versione corretta del test5.py con gestione errori migliorata
############################################################

import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import certifi
import logging

# Configurazione logging per debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ['SSL_CERT_FILE'] = certifi.where()

# Carichiamo le variabili di sistema
load_dotenv(override=True)

# Verifica delle chiavi API
openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY non trovata nel file .env")
if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY non trovata nel file .env")

print(f"OpenAI API Key: {openai_api_key[:8]}...")
print(f"DeepSeek API Key: {deepseek_api_key[:8]}...")

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

# Configurazione dei client con timeout e retry
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Creiamo il client DeepSeek con configurazioni robuste
deepseek_client = AsyncOpenAI(
    base_url=DEEPSEEK_BASE_URL, 
    api_key=deepseek_api_key,
    timeout=30.0,  # Timeout di 30 secondi
    max_retries=3   # Massimo 3 tentativi
)

# Creiamo il modello DeepSeek
deepseek_model = OpenAIChatCompletionsModel(
    model="deepseek-chat", 
    openai_client=deepseek_client
)

# Creiamo l'agente di vendita
sales_agent = Agent(
    name="DeepSeek sales agent",
    instructions=instructions1,
    model=deepseek_model
)

# Tool per l'invio email
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Invia una mail di vendita a freddo con uno specifico oggetto ed un corpo in html a prospect
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        from_email = Email("federico.tognetti@gmail.com")
        to_email = To("federico.tognetti@gmail.com")
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        logger.info(f"Email inviata con successo. Status: {response.status_code}")
        return {"status": "success", "status_code": response.status_code}
    except Exception as e:
        logger.error(f"Errore nell'invio email: {e}")
        return {"status": "error", "error": str(e)}

# Tool per scrivere l'oggetto
subject_instructions = (
    "Sei un copywriter esperto nello scrivere l'oggetto per una email di vendita a freddo."
    "Ti viene fornito un messaggio e devi scrivere un oggetto per una email che ha buone probabilità di essere aperta e ottenere una risposta."
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

# Tool per convertire in HTML
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

# Lista dei tool per la gestione della mail
email_tools = [send_html_email, subject_tool, html_tool]

# Agente per la gestione email
emailer_instructions = (
    "Sei esperto nel creare l'oggetto, formattare il corpo e spedire le email. Ricevi il corpo di una email da inviare."
    "Prima utilizzi il tool subject_writer per scrivere l'oggetto dell'email, poi utilizzi il tool html_converter per convertire il corpo in HTML."
    "Infine, utilizzi il tool send_html_email per inviare l'email con l'oggetto e il corpo HTML."
)

emailer_agent = Agent(
    name="Emailer agent",
    instructions=emailer_instructions,
    model="gpt-4o-mini",
    tools=email_tools,
    handoff_description="Genera l'oggetto, converti la mail e spediscila"
)

# Tool per l'agente di vendita
sales_tool = sales_agent.as_tool(
    tool_name="sales_agent",
    tool_description="Scrivi una mail di vendita a freddo"
)

async def send_dom_rev_formatted_mail():
    """
    Invia mail di vendita dopo aver scelto la miglior formulazione del testo.
    """
    
    sales_manager_instructions = """
    Sei un Sales Manager di Domus Revita. Il tuo obiettivo è creare una email di vendita a freddo efficace.
    
    Segui attentamente questi passaggi:
    1. Genera una Bozza: Utilizza il tool sales_agent per generare una bozza di email.
    
    2. Passaggio per l'Invio: Passa la bozza all'agente 'Email Manager'. L'Email Manager si occuperà della formattazione e dell'invio.
    
    Regole Fondamentali:
    - Devi utilizzare il tool sales agent per generare la bozza — non scriverla tu stesso e mantieni la lingua italiana.
    - Devi passare esattamente UNA email all'Email Manager.
    """

    sales_manager = Agent(
        name="Sales manager",
        instructions=sales_manager_instructions,
        model="gpt-4o-mini",
        tools=[sales_tool],
        handoffs=[emailer_agent]
    )

    message = "Scrivi ed invia una mail di vendita a freddo per un potenziale cliente che vuole riqualificare la sua casa"

    try:
        with trace("Mail formattata Domus Revita"):
            logger.info("Avvio del processo di invio email...")
            result = await Runner.run(sales_manager, message)
            print("✅ Processo completato con successo!")
            print(f"Risultato: {result.final_output}")
            return result
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {e}")
        print(f"❌ Errore: {e}")
        raise

async def main():
    """Funzione principale con gestione errori"""
    try:
        print("🚀 Avvio del sistema di invio email Domus Revita...")
        await send_dom_rev_formatted_mail()
    except Exception as e:
        print(f"💥 Errore critico: {e}")
        print("\n🔧 Suggerimenti per risolvere:")
        print("1. Verifica la connessione internet")
        print("2. Controlla che le chiavi API siano valide")
        print("3. Esegui test_connection.py per diagnosticare il problema")

if __name__ == "__main__":
    asyncio.run(main())

