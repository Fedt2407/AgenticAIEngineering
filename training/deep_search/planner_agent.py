from pydantic import BaseModel, Field
from agents import Agent

HOW_MANY_SEARCHES = 3

INSTRUCTIONS = f"Sei un assistente di ricerca. Data una query, proponi una serie di ricerche web \
da eseguire per rispondere al meglio alla query. Genera {HOW_MANY_SEARCHES} termini di ricerca."

# Definiamo la classe per le singole ricerche
class WebSearchItem(BaseModel):
    """Classe che definisce la struttura di un singolo elemento di ricerca web.
    
    Questa classe eredita da BaseModel di Pydantic e definisce i campi necessari
    per rappresentare una singola query di ricerca web con la sua motivazione.
    
    Attributes:
        - reason (str): La spiegazione del motivo per cui questa specifica ricerca
        è rilevante e importante per la query principale.
            
        - query (str): Il termine o la frase di ricerca effettiva da utilizzare
        per eseguire la ricerca sul web.
    """
    reason : str = Field(description="Spiega il motivo per cui questa ricerca è importante per la query")
    query : str = Field(description="Il termine di ricerca usato per la ricerca sul web")

# Definiamo la classe che descrive il piano di ricerca che contempla tutte le singole ricerche
class WebSearchPlan(BaseModel):
    """Classe che definisce il piano di ricerca web complessivo.
    
    Questa classe eredita da BaseModel di Pydantic e definisce la struttura
    per organizzare un insieme di ricerche web correlate a una query.
    
    Attributes:
        - searches (list[WebSearchItem]): Una lista di oggetti WebSearchItem,
        dove ogni elemento rappresenta una singola ricerca web pianificata
        con la sua motivazione. La lista contiene tutte le ricerche necessarie
        per rispondere in modo completo alla query originale.
    """
    searches : list[WebSearchItem] = Field(description="Una lista delle ricerche sul web per trovare la miglior risposta alla query")

# Definiamo l'agente di ricerca
planner_agent = Agent(
    name="Planner Agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o",
    output_type=WebSearchPlan
)