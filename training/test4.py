###############################################################
# In questo file viene terstato i laboratori 1 & 2 della week 2
###############################################################

# In questa sezione verranno applicati gli SDK di OpenAI per creare chimate più efficaci agli LLM
# Utilizzeremo la libreria agents

from time import sleep
from dotenv import load_dotenv
from agents import Agent, Runner, stream_events, trace
import asyncio
import os

# Ci assicuriamo di caricare le variabili ambientali
load_dotenv(override=True)

# Facciamo un esempio di funzione asincrona
async def shy_say_hello(name):
    """
    Una funzione asincrona dimostrativa che simula un ritardo prima di stampare un saluto.
    
    La funzione stampa un messaggio iniziale, attende 3 secondi in modo asincrono,
    e poi stampa "Hello". Serve come esempio base per illustrare l'uso di asyncio.
    """
    print("I just wanna say... ehm...")

    # IMPORTANTE: await può essere usato unicamente all'interno della funzione asincrona definita con "async def ..."
    await asyncio.sleep(3)
    print(f"Hello {name}")

# necessario chiamare la funzione in modo asincrono
# asyncio.run(shy_say_hello("Serena")) # Decommentare per eseguire

# Oppure è possibile eseguire la funzione asincrona utilizzando asyncio.run() direttamente nel blocco principale
# si utilizzerà il solito comando: python test4.py oppure: uv run python test4.py
# if __name__ == "__main__":
#     asyncio.run(shy_say_hello("Serena")) # Decommentare per eseguire


###########################################
# gateher per eseguire molteplici coroutine
###########################################

# QUESTO ESEGUE TUTTI I COMANDI IN PARALLELO (nota i task A e B hanno un ritardo tra loro si 0.5 secondi)
async def task(name, delay):
    await asyncio.sleep(delay)
    print(f"Task: {name} done after {delay} seconds")
    return name

async def main():
    results = await asyncio.gather(
        task("A", 1.5),
        task("B", 2),
        task("C", 3)
    )
    print(results)

# asyncio.run(main())

# ESERCIZIO 1
# Write a coroutine that:
# Takes a name
# Waits 2 seconds
# Prints “Hello, [name]!”

async def greet(name):
    await asyncio.sleep(2)
    print(f"Hello {name}")
# asyncio.run(greet("Serena")) # Decommentare per eseguire


# ESERCIZIO 2
# Write three async functions:
# fetch_data()
# process_data()
# save_data()
# Each should wait 1 second and return a string. Use asyncio.gather() to run all three.

async def fetch_data():
    await asyncio.sleep(1)
    print("Data fetched")
    return "Data fetched"

async def process_data():
    await asyncio.sleep(2)
    print("Data processed")
    return "Data processed"

async def save_data():
    await asyncio.sleep(3)
    print("Data saved")
    return "Data saved"

async def main():
    results = await asyncio.gather(
        fetch_data(),
        process_data(),
        save_data()
    )
    print(results)

# asyncio.run(main()) # Decommentare per eseguire

# ESERCIZIO 3
# Write a coroutine that counts down from 5 to 1 with a 1-second wait in between each number.

async def countdown(max, min):
    while max >= min:  
        await asyncio.sleep(1)
        print(max)
        max -= 1

# asyncio.run(countdown(5, 1))

# ESERCIZIO 4 - Compare Blocking vs Async

import time
def blocking_loop():
    start_time = time.time()
    for i in range(3):
        time.sleep(1)
        print(f"Blocking iteration {i+1}")
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Blocking loop done in {execution_time:.2f} seconds")
    return execution_time

async def non_blocking_loop():
    start_time = time.time()
    for i in range(3):
        await asyncio.sleep(1)
        print(f"Async iteration {i+1}")
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Async loop done in {execution_time:.2f} seconds")
    return execution_time

# Compare execution times
def compare_execution():
    print("Running blocking loop...")
    blocking_time = blocking_loop()
    
    print("\nRunning async loop...")
    async_time = asyncio.run(non_blocking_loop())
    
    print(f"\nBlocking took {blocking_time:.2f} seconds")
    print(f"Async took {async_time:.2f} seconds")

# compare_execution()
# Expected output:
# Blocking loop: ~3 seconds (sequential)
# Async loop: ~3 seconds (sequential)

# Una funzione definita con async def non è più una funzione ma una coroutine
# Una coroutine non eseguie la funzione ma restituisce un oggetto

# async def do_something() -> str:
#     return "Done!"

# my_coroutine = do_something()
# # print(my_coroutine) # Nel terminale riceveremo: <coroutine object do_something at 0x105a6d220> sys:1: RuntimeWarning: coroutine 'do_something' was never awaited

# async def main():
#     result = await my_coroutine # IMPORTANTE: await può essere solamente usato all'interno di una funzione asincrona 
#     print(result)
# # asyncio.run(main())

########################
# Lab 1 Week 2 del corso
########################

# Creiamo una is tanza di Agente
# NOTA: l'SDK di OpenAI è non "opinionated" significa che può funzionare anche con altri modelli non OpenAI

# VERSIONE SENZA TRACCIAMENTO
async def main():
    agent = Agent(
        name="Giullare",
        instructions="Sei un giullare molto bravo nel raccontare barzellette",
        model="gpt-4o-mini"
    )

# Per ottenere il risultato (un oggetto di Python) dobbiamo passare l'agente ed il prompt
# IMPORTANTE = essendo una coroutine (e non una funzione) dobbiamo usare await
    result = await Runner.run(agent, "Qual'è la barzelletta più divertente del mondo?")
    print(result.final_output) # usiamo final_output per passare solo la risposta dell'LLM senza informazioni aggiuntive

# asyncio.run(main()) # decommenta per eseguire

# VERSIONE CON TRACCIAMENTO
# Usando trace è possibile tracciare l'interazione del nostro codice con l'LLM. L'argomento passato a trace è il titolo del log es. trace("Giullare")
async def main():
    agent = Agent(
        name="Giullare",
        instructions="Sei un giullare molto bravo a raccontare barzellette",
        model="gpt-4o-mini"
    )

    # Abilitiamo il tracciamento:
    with trace("Giullare"):
        result = await Runner.run(agent, "Racconta una barzelletta divertente sull'Agentic AI")
        print (result.final_output)

# asyncio.run(main()) # decommenta per eseguire


######################################
# Lab 2 Week 2 del corso - SDK Project
######################################

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
import ssl
import certifi
from sendgrid.helpers.mail import Mail, Email, To, Content
os.environ['SSL_CERT_FILE'] = certifi.where() # inserito per risolvere l'errore SSL certificate di Sendgrid

# Carichiamo le variabili ambientali
load_dotenv(override=True)

# Facciamo un test per verificare che Sendgrid funzioni correttamente
def send_test_email():
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("federico.tognetti@gmail.com")  # Change to your verified sender
    to_email = To("federico.tognetti@gmail.com")  # Change to your recipient
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(response.status_code)

# send_test_email() # Decommenta per eseguire
 
######################################### 
# 1. Defiamo le istruzioni per il modello
# NOTA: sono i system prompts con cui diamo istruzioni ai diversi agenti
instructions1 = "Sei un agente di vendita che lavora per ComplAI, \
un'azienda che fornisce uno strumento SaaS per garantire la conformità SOC2 e preparare gli audit, basato sull'AI. \
Scrivi email fredde professionali e serie."

instructions2 = "Sei un agente di vendita umoristico e coinvolgente che lavora per ComplAI, \
un'azienda che fornisce uno strumento SaaS per garantire la conformità SOC2 e preparare gli audit, basato sull'AI. \
Scrivi email fredde argute e coinvolgenti che hanno più probabilità di ottenere una risposta."

instructions3 = "Sei un agente di vendita impegnato che lavora per ComplAI, \
un'azienda che fornisce uno strumento SaaS per garantire la conformità SOC2 e preparare gli audit, basato sull'AI. \
Scrivi email fredde concise e dirette al punto."

#################################################################################
# 2. Creiamo 3 agenti di vendita che risponderanno alle istruzioni definite sopra
sales_agent1 = Agent(
    name="Agente di vendita professionale",
    instructions=instructions1,
    model="gpt-4o-mini"
)

sales_agent2 = Agent(
    name="Agente di vendita spiritoso",
    instructions=instructions2,
    model="gpt-4o-mini"
)

sales_agent3 = Agent(
    name="Agente di vendita impegnato",
    instructions=instructions3,
    model="gpt-4o-mini"
)

######################################################################
# 3. Facciamo una prova di scrittura della mail da parte dell'agente 1
async def write_stream_mail():
    """
    Funzione asincrona che genera e stampa in streaming un'email di vendita a freddo utilizzando un agente di vendita.
    
    La funzione:
    - Utilizza l'agente sales_agent1 per generare un'email di vendita a freddo
    - Stampa il contenuto dell'email in tempo reale man mano che viene generato
    - Gestisce il flusso di eventi in streaming dalla risposta dell'agente
    
    Returns:
        None: La funzione stampa direttamente l'output senza restituire valori
    
    Raises:
        Potenziali eccezioni durante l'esecuzione asincrona o la comunicazione con il modello
    """
    # NOTA: run_streamed permette di mostrare i risultati (streaming) man mano che sono disponibili
    # IMPORTANTE: Il metodo Runner.run_streamed() non restituisce una coroutine, quindi non può essere usato con await
    result = Runner.run_streamed(sales_agent1, input="Scrivi un'email di vendita a freddo")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

# asyncio.run(write_stream_mail()) # Decommenta per eseguire

################################################
# 4. Facciamo funzionare i 3 agenti in parallelo

async def write_mails_in_parallel():
    """
    Funzione asincrona che genera in parallelo email di vendita a freddo utilizzando tre diversi agenti di vendita.
    
    La funzione:
    - Utilizza tre agenti di vendita con personalità diverse (professionale, spiritoso, impegnato)
    - Esegue le richieste in parallelo usando asyncio.gather()
    - Limita ogni email a un massimo di 50 parole
    - Stampa le tre email generate una dopo l'altra
    
    Returns:
        None: La funzione stampa direttamente gli output senza restituire valori
    
    Raises:
        Potenziali eccezioni durante l'esecuzione asincrona o la comunicazione con i modelli
    """
    message = "Scrivi una mail di vendita a freddo di massimo 50 parole"

    with trace("Mail di vendita in parallelo"):
        # Utilizziamo asyncio.gather per eseguire in parallelo le richieste dei tre agenti
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message)
        )

    outputs = [result.final_output for result in results]

    for output in outputs:
        print(output + "\n\n")

# asyncio.run(write_mails_in_parallel()) # Decommenta per esseguire

###############################################################################
# 5. Aggiungiamo un ulteriore agente che selezioni la migliore email di vendita
email_picker_instructions = (
    "Scegli la migliore email di vendita a freddo tra le opzioni fornite. "
    "Immagina di essere un cliente e scegli quella a cui saresti più propenso a rispondere. "
    "Non fornire spiegazioni; rispondi solo con l'email selezionata."  # Molto importante per evitare allucinazioni del modello
)

email_picker = Agent(
    name="Selezionatore email",
    instructions=email_picker_instructions,
    model="gpt-4o-mini"
)

async def write_best_sales_email():
    message = "Scrivi una mail di vendita a freddo di massimo 40 parole"

    with trace("Miglior mail di vendita:"):
        # Usiamo .gather per eseguire tutti gli agenti in parallelo
        # NOTA: tutti i processi a seguire vengono tracciati sotto lo stesso trace per avere una visione complessiva
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message)
        )

        outputs = [result.final_output for result in results]
        sales_emails = "Email di vendita:\n\n".join(outputs)
        # Await the runner call
        best_email = await Runner.run(email_picker, sales_emails)
        print(f"La migliore email di vendita è:\n\n{best_email.final_output}")

# asyncio.run(write_best_sales_email()) # Decommenta per eseguire

##################################################################################################################
# 6. Aggiungiamo la possibilità di usare i tool utilizzando il decoratore @function_tool al posto del formato JSON

# Il decoratore ci evita di dover scrivere il lungo e articolato file JSON
@function_tool
def send_email(body: str):
    """
    Invia una email utilizzando l'API di SendGrid.
    
    Args:
        body (str): Il contenuto del corpo dell'email da inviare
        
    Returns:
        dict: Un dizionario contenente lo stato dell'invio {'status': 'success'}
        
    Note:
        - Utilizza le credenziali SendGrid memorizzate nelle variabili d'ambiente
        - Sia l'indirizzo mittente che destinatario sono preimpostati
        - Il soggetto dell'email è fisso come "Mail di vendita"
    """
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("federico.tognetti@gmail.com")
    to_email = To("federico.tognetti@gmail.com")
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Mail di vendita", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "sucess"}

# IMPORTANTE: è possibile trasformare un intero agente usando il metodo .as_tool
# Trasformiamo gli agenti di vendita in tool, la descrione può essere la medesima per tutti i tool

tool_description = "Scrivi una mail di vendita a freddo"

tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1",
    tool_description=tool_description
)

tool2 = sales_agent2.as_tool(
    tool_name="sales_agent2",
    tool_description=tool_description
)

tool3 = sales_agent3.as_tool(
    tool_name="sales_agent3",
    tool_description=tool_description
)

# Alla lista dei tool è stato aggiunto il tool che nasce dalla funzione con decoratore @function_tool
tools = [tool1, tool2, tool3, send_email]
    
################################################################################
# 7. Creiamo adesso l'agente sales manager che può usare i tool definiti poco fa

async def write_email_with_tools():

    sales_manager_instructions = """
    Sei un Sales Manager di ComplAI. Il tuo obiettivo è trovare la migliore email di vendita a freddo utilizzando i tool sales_agent.

    Segui attentamente questi passaggi:
    1. Genera le Bozze: Utilizza tutti e tre i tool sales_agent per generare tre diverse bozze di email. Non procedere finché non hai tutte e tre le bozze pronte.
    2. Valuta e Seleziona: Esamina le bozze e scegli la singola email migliore basandoti sul tuo giudizio di quale sia la più efficace.
    3. Usa il tool send_email per inviare la migliore email (e solo la migliore) all'utente.

    Regole Fondamentali:
    - Devi usare i tool sales_agent per generare le bozze — non scriverle tu stesso.
    - Devi inviare UNA SOLA email usando il tool send_email — mai più di una.
    """

    sales_manager = Agent(
        name="Responsabile vendite",
        instructions=sales_manager_instructions,
        tools=tools,
        model="gpt-4o-mini"
    )

    message = "Scrivi una mail di vendita a freddo al CEO di una azienda cliente"

    with trace("Email di vendita con tools"):
        result = await Runner.run(sales_manager, message)
        print(result.final_output) # stampa unicamente l'output senza informazioni aggiuntive a corredo

# asyncio.run(write_email_with_tools()) # Decommenta per eseguire

###############################################
# 8. Creiamo ori tools per gestire la richiesta

# Per prima cosa definiamo gli handoff
subject_instructions = (
    "Sei un copywriter esperto nello scrivere l'oggetto per una email di vendita a freddo."
    "Ti viene fornito un messaggio e devi scrivere un oggetto per una email che ha buone probabilità di essere aperta ottenere una risposta."
)

html_instructions = (
    "Sei un esperto nel convertire il corpo di una email testuale in un corpo email HTML."
    "Ti viene fornito il corpo di una email testuale che potrebbe contenere dei markdown"
    "Devi convertirlo in un corpo email HTML con un layout e un design elaborato, chiaro e convincente."
)

# Definiamo due nuovi agenti
subject_writer = Agent(
    name="Copywriter oggetto email",
    instructions=subject_instructions,
    model="gpt-4o-mini"
)

html_converter = Agent(
    name="Convertitore in html",
    instructions=html_instructions,
    model="gpt-4o-mini"
)

# Trasformiamo i  due nuovi agenti in tool usando il metodo .as_tool
subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Scrivi l'oggetto per una mail di vendita a freddo"
)

html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Trasformai il corpo testuale di una email in html"
)

#  Adesso scriveremo invece un tool da una funzione per inviare la mail con Sendgrid
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]: 
    """
    Invia una mail con l'oggetto ricevuto ed il corpo in html al cliente prospect
    Usa i paramtri oggetto e body che sono stati gestiti dai precedenti tool dedicati
    """
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("federico.tognetti@gmail.com")
    to_email = To("federico.tognetti@gmail.com")
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

# Definiamo la lista dei tools
tools = [subject_tool, html_tool, send_html_email]


###########################################################
# 9. Creiamo ora l'handoff a cui verrà delegato il processo

# Un Handoff è un agente specializzato a cui l'agente principale può delegare compiti particolari specifici per cui l'handoff è progettato
# IMPORTANTE: 
# - quando l'agente principale usa un tool (che può essere a sua volta un'agente) il flusso gli output generati dal tool
# ritorna all'agente principale che mantiene il controllo del processo per continuare il workflow
# - quando l'agente principale delega un task ad un handoff il controllo viene ceduto a quest'ultimo e gli output generati non tornano
# più all'agente principale (che di fatto termina la gestione del workflow delegando all'handoff) 

# Definiamo le istruzioni dell'handoff
handoff_instructions = (
    "Sei un formattatore e mittente di email. Ricevi il corpo di un'email da inviare."
    "Prima utilizza il tool subject_writer per scrivere l'oggetto dell'email, poi usa il tool html_converter per convertire il corpo in HTML."
    "Infine, utilizza il tool send_html_email per inviare l'email con l'oggetto e il corpo HTML."
)

# Definiamo l'handoff vero e proprio
emailer_agent = Agent(
    name="Agente per l'invio delle email formattate",
    instructions=handoff_instructions,
    tools=tools,
    model="gpt-4o-mini",
    handoff_description="Definisce l'oggeto di una email, converte il corpo in HTML e la invia al destinatario"
)

# Ricapitoliamo la lista dei tool e degli handoff del nostro agente principale
# NOTA: l'handoff è un agente che ha a sua volta dei tool al suo interno (alcuni sono a loro volta agenti e uno è una funzione concertita in tool)

tools = [tool1, tool2, tool3]
handoff = [emailer_agent]

# Definiamo infine l'egente principale che gestirà l'intero processo compreso il passaggio all'handoff per l'attività finale
async def send_formatted_mail():

    sales_manager_instructions = """
    Sei un Sales Manager di ComplAI. Il tuo obiettivo è trovare la migliore email di vendita a freddo utilizzando i tools del sales_agent.

    Segui attentamente questi passaggi:
    1. Genera le Bozze: Utilizza tutti e tre i tools del sales_agent per generare tre diverse bozze di email. Non procedere finché non hai pronte tutte e tre le bozze.

    2. Valuta e Seleziona: Esamina le bozze e scegli la singola email migliore basandoti sul tuo giudizio di quale sia la più efficace.
    Puoi utilizzare i tools più volte se non sei soddisfatto dei risultati del primo tentativo.

    3. Passaggio per l'Invio: Passa SOLO la bozza vincente all'agente 'Email Manager'. L'Email Manager si occuperà della formattazione e dell'invio.

    Regole Fondamentali:
    - Devi utilizzare i tools del sales agent per generare le bozze — non scriverle tu stesso.
    - Devi passare esattamente UNA email all'Email Manager — mai più di una.
    """

    sales_manager = Agent(
        name="Sales manager",
        instructions=sales_manager_instructions,
        model="gpt-4o-mini",
        tools=tools,
        handoffs=handoff
    )

    message = "Invia una mail di vendita a freddo al CEO di una azienda prospect"

    with trace("Mail formattata con handoff"):
        result = await Runner.run(sales_manager, message)
        print(result.final_output)

asyncio.run(send_formatted_mail())