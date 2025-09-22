from pydantic import BaseModel, Field
from agents import Agent

writer_agent_instructions = (
    "Sei un ricercatore senior incaricato di scrivere un report coerente per una query di ricerca. "
    "Ti verranno forniti la query originale e alcune ricerche iniziali fatte da un assistente di ricerca."
    "Per prima cosa dovresti creare una struttura per il report che ne descriva l'organizzazione e il flusso."
    "Poi, genera il report e restituiscilo come output finale." 
    "L'output finale deve essere in formato markdown e deve essere lungo e dettagliato."
    "L'obbiettivo è da 5-10 pagine di contenuto, almeno 1000 parole."
)

# Classe per definire la struttura dell'output
class ReportData(BaseModel):
    """Classe che definisce la struttura del report generato dall'agente writer.
    
    Questa classe eredita da BaseModel di Pydantic e definisce i campi necessari
    per strutturare il report di ricerca in modo organizzato e completo.
    
    Attributes:
        - short_summary (str): Un breve riassunto dei risultati principali della ricerca,
        contenuto in 2-3 frasi concise che catturano i punti chiave.
            
        - markdown_report (str): Il report completo in formato markdown, contenente
        l'analisi dettagliata, le argomentazioni e le conclusioni della ricerca.
        Include tutte le sezioni definite nell'outline iniziale.
            
        - follow_up_questions (list[str]): Una lista di domande e argomenti correlati
        che potrebbero essere interessanti da approfondire in future ricerche.
        Aiuta a identificare potenziali direzioni per espandere l'analisi.
    """
    short_summary : str = Field(description="Una breve introdione si risultati di 2-3 frasi")
    markdown_report : str = Field(description="Il report completo")
    follow_up_questions : list[str] = Field(description="Una lista degli argomenti correlati suggeriti") # Si specifica che ci si aspetta una lista di stringhe

# Definizione dell'agente
writer_agent = Agent(
    name="Writer agent",
    instructions=writer_agent_instructions,
    model="gpt-4o",
    output_type=ReportData # Questo parametro obbliga l'LLM di fornire un output strutturato come la classe Pydantic e non in formato testo di default
)