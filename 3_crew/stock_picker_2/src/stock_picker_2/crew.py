from re import A, T
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field, config # Usato per generare output strutturati
from crewai_tools import SerperDevTool
from .tools.push_tool import PushNotificationTool # Importiamo il tool customizzato

# IMPORT per usare la memoria in CrewAI
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

# PYDANTIC CLASSES ###############################################################
# Creiamo un classe pydantic che definisce ciascuna trending company
class TrendingCompany(BaseModel):
    """
    A company that is in the news and is attracting attention.
    """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")

# Creaimo la classe pydantic che raggruppa tutte le trending companies
class TrendingCompanyList(BaseModel):
    """
    A list of multiple trending companied that are in the news.
    """
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")

# Creiamo adesso una classe pydantic che definisce lo schema per la ricerca
class TrendingCompanyResearch(BaseModel):
    """
    Detailed research for a company
    """
    name: str = Field(description="Comapany name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospective")
    investment_potential: str = Field(description="Investment potential and sustainability for investment")

# Creiamo adesso una classe pydantic che definisce la lista delle ricerche effettuate
class TrendingCompanyResearchList(BaseModel):
    """
    A list of detailed research on all the companies
    """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")

# CREW CLASS #######################################################################
@CrewBase
class StockPicker2():
    """StockPicker2 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],  # type: ignore[index]
            tools=[SerperDevTool()]
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'], # type: ignore[index]
            tools=[PushNotificationTool()], # A questo agente viene attribuito il tool customizzato
            memory=True
        )

    # NOTA: l'agente manager non viene definito in seguito e usato per coordinare il processo gerarchico "hierarchical" e non "sequential"
    # @agent
    # def manager(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['manager'] # type: ignore[index]
    #     )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
            # output_file='output/decision.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker2 crew"""

        # Creiamo il manager separatamente
        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        # Definiamo la memoria a breve termine
        short_term_memory = ShortTermMemory(
            storage = RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small" # viene usato per creare gli embeddings necessari al DB vettoriale
                    }
                },
                type="short_term",
                path="./memory/"
            )
        )

        # Creiamo la memoria a breve termine
        long_term_memory = LongTermMemory(
            storage = LTMSQLiteStorage(
                db_path="./memory/long_term_memory_storage.db"
            )
        )

        # Creaimo la memoria di entity che usa le stesse logiche della memoria a breve termine
        entity_memory = EntityMemory(
            storage = RAGStorage(
                embedder_config={
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small"
                    }
                },
                type="short_term",
                path="./memory/"
            )
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager, # usiamo questo paramento per indicare "manger" come l'agente che gestirà il workflow (simile all'handoff nell'SDK di OpenAI)
            memory=True, # Serve ad abilitare la memoria del crew
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory,
            entity_memory=entity_memory
        )
