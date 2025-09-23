from tabnanny import verbose
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class Coder2():
    """Coder2 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Creiamo l'agente
    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'],
            verbose=True,
            allow_code_execution=True,  # Permette all'agente di esegurire il codice
            code_execution_mode="safe", # Fa si che il codice sia eseguita in un container Docker
            max_execution_time=30,      # Limita il tempo di esecuzione a massimo 30 secondi
            max_retry_limit=5           # Limita il numero di tentativi a 5
        )

    @task
    def task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'],
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates the Coder crew
        """

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
