import chunk
import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)

# Lanciamo la funsione asincrona con il monitoraggio dei vari step (chunk) grazie a yield
async def run(query: str):
    """
    Esegue una ricerca approfondita su un argomento e restituisce aggiornamenti in tempo reale.
    Questa funzione asincrona utilizza il ResearchManager per eseguire una ricerca completa,
    restituendo progressivamente gli stati di avanzamento e i risultati attraverso un generatore asincrono.

    Args:
        query (str): La query di ricerca su cui effettuare l'analisi approfondita

    Yields:
        str: Restituisce in sequenza:
            - URL per visualizzare il trace della ricerca
            - Messaggi di stato sull'avanzamento del processo
            - Report finale in formato markdown

    Note:
        La funzione utilizza yield per fornire aggiornamenti in tempo reale sullo stato del processo,
        permettendo di monitorare l'avanzamento della ricerca attraverso le varie fasi:
        pianificazione, ricerca, generazione report e invio email.
    """
    async for chunk in ResearchManager().Run(query):
        yield chunk


# Lanciamo l'interfaccia di Gradio per una visualizzaione a schermno
# Creiamo un'interfaccia grafica usando Gradio Blocks con un tema azzurro
with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    # Aggiungiamo un titolo in formato Markdown
    gr.Markdown("# Deep Research")
    
    # Creiamo una casella di testo per inserire la query di ricerca
    query_textbox = gr.Textbox("Quale argomento vuoi ricercare?")
    
    # Aggiungiamo un pulsante primario per avviare la ricerca
    search_button = gr.Button("Ricerca", variant="primary")
    
    # Area dove verrà mostrato il report in formato Markdown
    report = gr.Markdown(label="Report")

    # Quando si clicca il pulsante di ricerca, esegue la funzione run
    # passando il testo della query come input e mostrando il risultato nel report
    search_button.click(
        fn=run,
        inputs=query_textbox,
        outputs=report
    )

    # Permette di avviare la ricerca anche premendo Invio nella casella di testo
    # usando gli stessi parametri del pulsante di ricerca
    query_textbox.submit(
        fn=run,
        inputs=query_textbox,
        outputs=report
    )

# Avvia l'interfaccia web aprendola automaticamente nel browser predefinito
ui.launch(inbrowser=True)