from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
import asyncio

class ResearchManager:

    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report
        
        Il comando yield è simile a return ma invece di terminare la funzione, 
        "sospende" temporaneamente l'esecuzione e restituisce un valore.
        Questo permette di:
        
        1. Fornire aggiornamenti in tempo reale sullo stato del processo
        2. Riprendere l'esecuzione da dove era stata sospesa
        3. Creare una sorta di "stream" di dati che vengono prodotti man mano
        
        In questo codice specifico:
        - Ogni yield restituisce un messaggio di stato che può essere mostrato all'utente
        - Il codice continua a eseguire dopo ogni yield
        - L'ultimo yield restituisce il report finale completo
        """
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            # Primo yield: URL per visualizzare il trace
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            # Secondo yield: notifica che la pianificazione è completata
            yield "Searches planned, starting to search..."     
            
            search_results = await self.perform_searches(search_plan)
            # Terzo yield: notifica che le ricerche sono completate
            yield "Searches complete, writing report..."
            
            report = await self.write_report(query, search_results)
            # Quarto yield: notifica che il report è stato scritto
            yield "Report written, sending email..."
            
            await self.send_email(report)
            # Quinto yield: notifica che l'email è stata inviata
            yield "Email sent, research complete"
            
            # Ultimo yield: restituisce il report finale in markdown
            yield report.markdown_report
        

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")
        return report