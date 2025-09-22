from agents import Agent, WebSearchTool, ModelSettings

search_agent_instructions = (
    "Sei un assistente per la ricerca di contenuti sul web. Dato un termine di ricerca, cerchi sul web quel termine e "
    "produci un riassunto conciso dei risultati. Il riassunto deve essere di 2-3 paragrafi e meno di 300 "
    "parole. Cattura i punti principali. Scrivi in modo sintetico, non è necessario avere frasi complete o "
    "una grammatica perfetta. Questo sarà utilizzato da qualcuno che sta sintetizzando un report, quindi è "
    "vitale che tu catturi l'essenza e ignori tutto ciò che è superfluo. Non includere alcun commento aggiuntivo "
    "oltre al riassunto stesso."
)

search_agent = Agent(
    name="Search agent",
    instructions=search_agent_instructions,
    model="gpt-4o-mini",
    tools=[WebSearchTool(search_context_size="low")],
    model_settings=ModelSettings(tool_choice="required")
)