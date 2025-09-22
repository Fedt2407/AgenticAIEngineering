import asyncio
from agents import Runner, trace, gen_trace_id

# Importiamo i 4 agenti creati e le loro classi pydantic
from email_agent import email_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData

class ResearchManager:
    """
    Gestisce un workflow complesso di agenti per eseguire ricerche approfondite su un argomento.
    Questa classe è stata creata per orchestrare l'interazione tra diversi agenti specializzati,
    ognuno con un compito specifico nel processo di ricerca. 
    
    L'utilizzo di una classe permette di:
    1. Mantenere lo stato e il contesto tra le diverse fasi del workflow
    2. Incapsulare la logica di coordinamento tra gli agenti
    3. Fornire un'interfaccia pulita e coerente per l'esecuzione dell'intero processo
    4. Facilitare il riutilizzo del workflow in diverse parti dell'applicazione
    5. Gestire in modo centralizzato il tracciamento e il logging delle operazioni

    Il workflow completo include:
    - Pianificazione delle ricerche (planner_agent)
    - Esecuzione delle ricerche web (search_agent)
    - Generazione di report (writer_agent)
    - Invio email dei risultati (email_agent)

    Attributes:
        Nessun attributo di istanza richiesto poiché la classe agisce come orchestratore
        degli agenti importati.
    """

    async def Run(self, query: str):
        
        trace_id = gen_trace_id()
        
        # Terremo traccia e del processo tramite print e yield
        # Il comando yield è simile a return ma invece di terminare la funzione,
        # "sospende" temporaneamente l'esecuzione e restituisce un valore.
        # Questo permette di:
        # 1. Fornire aggiornamenti in tempo reale sullo stato del processo
        # 2. Riprendere l'esecuzione da dove era stata sospesa
        # 3. Creare una sorta di "stream" di dati che vengono prodotti man mano
        with trace("Reaserch Manager", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            # Da qui in avanti verrà tenuto tracci delle azioni intraprese dai vari metodi
            search_plan = await self.plan_searches(query)
            yield "Ricerca pianificata, inizio la ricerca..."

            search_results = await self.perform_searches(search_plan)
            yield "Ricerca completata, inizio la stesura del report..."

            report = await self.write_report(query, search_results)
            yield "Ho completato il report, preparo la mail..."

            await self.send_email(report)
            yield "Ho iviato la mail"

            yield report.markdown_report


    #########################################################################################
    # Lista dei metodi di questa classe
    #########################################################################################
    async def plan_searches(self, query : str) -> WebSearchPlan:
        """Pianifica le ricerche da effettuare per rispondere alla query.
        Questo metodo asincrono utilizza il planner_agent per generare un piano
        strutturato di ricerche web necessarie per rispondere in modo completo
        alla query fornita.

        Args:
            query (str): La query di ricerca per cui pianificare le ricerche

        Returns:
            WebSearchPlan: Un oggetto contenente la lista delle ricerche pianificate,
            dove ogni ricerca include il termine di ricerca e la motivazione (reason e query)

        Note:
            Il piano di ricerca viene generato utilizzando un modello LLM attraverso
            il planner_agent che analizza la query e determina le ricerche più rilevanti
            da effettuare.
        """
        print("Inizio la ricerca")
        result = await Runner.run(
            planner_agent,      # Agente definito in file separato ed importato nella classe
            f"Query: {query}"   # Messaggio / prompt da fornire all'agente
        )
        print(f"Stiamo facendo {len(result.final_output.searches)} ricerche")
        return result.final_output_as(WebSearchPlan)

    #########################################################################################
    async def perform_searches(self, search_plan=WebSearchPlan) -> list[str]:
        """Esegue le ricerche pianificate in parallelo utilizzando asyncio.
        Questo metodo asincrono prende il piano di ricerca generato da plan_searches
        ed esegue tutte le ricerche in parallelo utilizzando asyncio.create_task e
        as_completed per massimizzare l'efficienza.

        Args:
            search_plan (WebSearchPlan): Il piano di ricerca contenente la lista delle ricerche da eseguire

        Returns:
            list[str]: Lista dei risultati delle ricerche completate con successo.
            Le ricerche fallite vengono omesse dal risultato finale.

        Note:
            - Utilizza asyncio per eseguire le ricerche in parallelo
            - Tiene traccia dell'avanzamento e lo stampa
            - Gestisce i fallimenti delle singole ricerche senza interrompere il processo
        """
        print("Sto cercando...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Sto cercando... {num_completed/len(tasks)} completati")
        print("Ho completato la ricerca")
        return results

    #########################################################################################
    async def search(self, item : WebSearchItem) -> str | None: # esplicita che il risultato atteso può essere una stringa oppure None
        """Esegue una singola ricerca web utilizzando il search_agent.
        Questo metodo asincrono prende un singolo elemento di ricerca (WebSearchItem) ed esegue
        la ricerca utilizzando il search_agent. Il metodo formatta il messaggio di input
        combinando il termine di ricerca e la motivazione, e gestisce eventuali errori
        durante l'esecuzione.

        Args:
            item (WebSearchItem): Un oggetto contenente il termine di ricerca (query) 
            e la motivazione (reason) per quella specifica ricerca

        Returns:
            str | None: Il risultato della ricerca come stringa se ha successo,
            None se si verifica un errore durante l'esecuzione

        Note:
            - Il metodo è asincrono e utilizza Runner.run per eseguire il search_agent
            - Gestisce le eccezioni durante l'esecuzione della ricerca
            - Formatta il messaggio di input in un formato specifico per il search_agent
        """
        message = f"Termine di ricerca{item.query}\nMotivazione della ricerca{item.reason}"
        try:
            result = await Runner.run(
                search_agent,   # Agente definito in un file separato e importata qui
                message         # Messaggio / prompt da fornire all'agente per chiedere di eseguire il task 
            )
            return str(result.final_output)
        
        except Exception as e:
            print(f"Errore rilevato: {e}")
            return None

    #########################################################################################
    async def write_report(self, query : str, search_results : list[str]) -> ReportData:
        """Genera un report strutturato basato sui risultati delle ricerche web.       
        Questo metodo asincrono utilizza il writer_agent per generare un report completo
        basato sulla query originale e sui risultati delle ricerche effettuate. Il report
        viene restituito come oggetto ReportData strutturato.

        Args:
            query (str): La query di ricerca originale dell'utente
            search_results (list[str]): Lista dei risultati ottenuti dalle ricerche web

        Returns:
            ReportData: Un oggetto contenente il report strutturato in formato markdown
            e altre informazioni correlate

        Note:
            - Il metodo è asincrono e utilizza Runner.run per eseguire il writer_agent
            - Formatta i dati di input combinando query e risultati in un unico messaggio
            - Converte l'output finale nel tipo ReportData
        """
        print("Sto elaborando il report...")
        message = f"Chiave di ricerca {query} riassunta nei risultati: {search_results}"
        result = await Runner.run(
            writer_agent,
            message
        )
        print("Ho completato la stesura del report")
        return result.final_output_as(ReportData)

    #########################################################################################
    async def send_email(self, report : ReportData) -> None:
        """Invia via email il report generato utilizzando l'email_agent.
        Questo metodo asincrono si occupa di inviare il report finale via email
        utilizzando l'email_agent. Il report viene inviato nel formato markdown.

        Args:
            report (ReportData): L'oggetto contenente il report da inviare via email

        Returns:
            None: Il metodo non restituisce nulla ma ritorna l'oggetto report originale

        Note:
            - Il metodo è asincrono e utilizza Runner.run per eseguire l'email_agent
            - Utilizza il campo markdown_report dell'oggetto ReportData come contenuto dell'email
            - Stampa messaggi di log per tracciare l'avanzamento dell'invio
        """
        print("Sto inviando la mail...")
        result = await Runner.run(
            email_agent,
            report.markdown_report
        )
        print("Mail inviata")
        return report