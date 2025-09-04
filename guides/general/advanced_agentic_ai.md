# Guida Avanzata all'Agentic AI

## Handoff, Guardrails, Structured Tools e Concetti Teorici Fondamentali

---

## Sommario

1. [Handoff Pattern nell'Agentic AI](#handoff-pattern)
2. [Guardrails: Sicurezza e Controllo](#guardrails)
3. [Structured Tools con Pydantic](#structured-tools)
4. [Schema Pydantic per Output Strutturati](#pydantic-schemas)
5. [Multi-Agent Orchestration](#multi-agent-orchestration)
6. [Chain of Thought e Reasoning Patterns](#chain-of-thought)
7. [Context Management e Memory Systems](#context-management)
8. [Agent Specialization e Role-Based Architecture](#agent-specialization)
9. [Error Recovery e Resilience Patterns](#error-recovery)
10. [Performance Optimization Strategies](#performance-optimization)

---

## 1. Handoff Pattern nell'Agentic AI {#handoff-pattern}

### Concetti Teorici

Il **pattern di handoff** è un meccanismo fondamentale nell'architettura multi-agente che consente il trasferimento controllato dell'esecuzione da un agente a un altro. Questo pattern è essenziale per:

- **Specializzazione**: Ogni agente gestisce compiti specifici del proprio dominio
- **Scalabilità**: Distribuzione del carico di lavoro tra agenti specializzati
- **Manutenibilità**: Separazione delle responsabilità e logiche di business
- **Resilienza**: Isolamento degli errori per evitare fallimenti a cascata

#### Tipologie di Handoff

1. **Sequential Handoff**: Trasferimento lineare tra agenti in sequenza predefinita
2. **Conditional Handoff**: Trasferimento basato su condizioni dinamiche
3. **Hierarchical Handoff**: Trasferimento tra livelli gerarchici (supervisore → specialista)
4. **Collaborative Handoff**: Trasferimento temporaneo per collaborazione

### Implementazione Pratica

```python
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json

# Definiamo una classe HandoffReason che eredita da Enum
# Enum è una classe speciale di Python che ci permette di definire un insieme fisso di costanti
# In pratica Enum è una classe base a cui appicare il principio di ereditarietà delle classi come la classe Studente che eredita da Persona def Studente(Persona):
class HandoffReason(Enum):
    """Ragioni per cui avviene un handoff."""
    # Ogni riga qui sotto definisce una costante dell'enumerazione
    # A sinistra dell'= c'è il nome della costante che useremo nel codice
    # A destra c'è il valore effettivo associato a quella costante

    # Questa costante indica che serve un agente specializzato
    SPECIALIZATION_REQUIRED = "specialization_required"
    # Questa costante indica che il task è stato completato
    TASK_COMPLETED = "task_completed"
    # Questa costante indica che si sta gestendo un errore
    ERROR_RECOVERY = "error_recovery"
    # Questa costante indica che l'handoff è stato richiesto dall'utente
    USER_REQUEST = "user_request"
    # Questa costante indica che ci sono vincoli di risorse
    RESOURCE_CONSTRAINT = "resource_constraint"

    # Usando Enum, possiamo:
    # 1. Avere un insieme predefinito e limitato di valori possibili
    # 2. Evitare errori di digitazione usando le costanti invece delle stringhe
    # 3. Avere autocompletamento nell'IDE
    # 4. Fare confronti in modo più sicuro

# Il decoratore @dataclass è una funzionalità di Python che automatizza la creazione di classi per contenere dati
# In particolare:
# 1. Genera automaticamente __init__() con tutti gli attributi definiti come variabili di classe
# 2. Genera automaticamente __repr__() per una rappresentazione leggibile della classe
# 3. Genera automaticamente __eq__() per confrontare istanze della classe
# 4. Genera automaticamente __hash__() se specificato frozen=True
# 5. Riduce il boilerplate code necessario per creare classi di dati
# 6. Rende il codice più pulito e manutenibile
@dataclass
class HandoffContext:
    """Contesto trasferito durante l'handoff."""
    from_agent: str
    to_agent: str
    reason: HandoffReason
    data: Dict[str, Any]
    conversation_history: List[Dict]
    metadata: Dict[str, Any]
    priority: int = 1

# Senza @dataclass avremmo dovuto scrivere:
#
# class HandoffContext:
#     """Contesto trasferito durante l'handoff."""
#     def __init__(self, from_agent: str, to_agent: str, reason: HandoffReason,
#                  data: Dict[str, Any], conversation_history: List[Dict],
#                  metadata: Dict[str, Any], priority: int = 1):
#         self.from_agent = from_agent
#         self.to_agent = to_agent
#         self.reason = reason
#         self.data = data
#         self.conversation_history = conversation_history
#         self.metadata = metadata
#         self.priority = priority
#
#     def __repr__(self):
#         return (f"HandoffContext(from_agent={self.from_agent!r}, "
#                f"to_agent={self.to_agent!r}, reason={self.reason!r}, "
#                f"data={self.data!r}, conversation_history={self.conversation_history!r}, "
#                f"metadata={self.metadata!r}, priority={self.priority!r})")
#
#     def __eq__(self, other):
#         if not isinstance(other, HandoffContext):
#             return NotImplemented
#         return (self.from_agent == other.from_agent and
#                self.to_agent == other.to_agent and
#                self.reason == other.reason and
#                self.data == other.data and
#                self.conversation_history == other.conversation_history and
#                self.metadata == other.metadata and
#                self.priority == other.priority)

class AgentOrchestrator:
    """Orchestratore per la gestione degli handoff tra agenti."""

    # Inizializza le strutture dati vuote per:
    # - agents: dizionario che conterrà gli agenti registrati
    # - handoff_rules: dizionario per le regole di trasferimento tra agenti
    # - active_sessions: dizionario per tenere traccia delle sessioni attive
    # Queste strutture verranno popolate tramite i metodi register_agent(), define_handoff_rule() e exceute_handoff()
        self.agents = {}
        self.handoff_rules = {}
        self.active_sessions = {}

    # Questo metodo registra un nuovo agente nel sistema specificando il suo nome, l'istanza e le sue capacità
    def register_agent(self, name: str, agent_instance, capabilities: List[str]):
        """Registra un agente con le sue capacità."""
        self.agents[name] = {
            'instance': agent_instance,
            'capabilities': capabilities,
            'status': 'idle'
        }

    # Questo metodo definisce le regole per il trasferimento delle richieste tra agenti, specificando:
    # - l'agente di origine (from_agent)
    # - l'agente di destinazione (to_agent)
    # - la funzione che determina quando effettuare il trasferimento (condition_func)
    # - la priorità della regola (priority)
    def define_handoff_rule(self, from_agent: str, to_agent: str, condition_func, priority: int = 1):
        """Definisce regola di handoff tra agenti."""
        if from_agent not in self.handoff_rules:
            self.handoff_rules[from_agent] = []

        self.handoff_rules[from_agent].append({
            'to_agent': to_agent,
            'condition': condition_func,
            'priority': priority
        })

    # Questo metodo esegue il trasferimento di controllo tra un agente e l'altro, verificando che:
    # - gli agenti esistano nel sistema
    # - l'agente target abbia le capacità richieste
    # - aggiorna lo stato degli agenti coinvolti
    # - restituisce il risultato del trasferimento
    def execute_handoff(self, context: HandoffContext) -> Dict[str, Any]:
        """Esegue l'handoff tra agenti."""
        from_agent = self.agents.get(context.from_agent)
        to_agent = self.agents.get(context.to_agent)

        if not from_agent or not to_agent:
            raise ValueError("Agenti non trovati per handoff")

        # Validazione capacità dell'agente target
        required_capability = context.metadata.get('required_capability')
        if required_capability and required_capability not in to_agent['capabilities']:
            return {
                'status': 'failed',
                'reason': 'missing_capability',
                'required': required_capability
            }

        # Trasferimento dello stato
        handoff_result = to_agent['instance'].receive_handoff(context)

        # Aggiorna stati
        from_agent['status'] = 'idle'
        to_agent['status'] = 'active'

        return {
            'status': 'success',
            'handoff_id': f"{context.from_agent}_{context.to_agent}_{hash(str(context.data))}",
            'result': handoff_result
        }

# Esempio di agente con supporto handoff
class SpecializedAgent:
    """Agente specializzato con capacità di handoff."""

    # Inizializza la classe con nome, specializzazione e orchestratore che gestisce gli handoff tra agenti
    def __init__(self, name: str, specialization: str, orchestrator: AgentOrchestrator):
        self.name = name
        self.specialization = specialization
        self.orchestrator = orchestrator
        self.context = None

    # Questo metodo permette di riceve il trasferimento di controllo da un altro agente
    def receive_handoff(self, context: HandoffContext) -> Dict[str, Any]:
        """Riceve handoff da altro agente."""
        self.context = context

        print(f"Agent {self.name} ricevuto handoff da {context.from_agent}")
        print(f"Ragione: {context.reason.value}")

        # Processa il compito basandosi sul contesto ricevuto
        return self.process_task(context.data)

    # Questo metodo processa il compito ricevuto in base alla specializzazione dell'agente.
    # Se la specializzazione non corrisponde, restituisce un errore.
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa il compito ricevuto via handoff."""
        # Logica specifica dell'agente
        if self.specialization == "data_analysis":
            return self.analyze_data(task_data)
        elif self.specialization == "text_processing":
            return self.process_text(task_data)

        return {"status": "unknown_task", "specialization": self.specialization}

    # Questo metodo crea un contesto di handoff e inizia il trasferimento del controllo verso l'agente di destinazione
    def initiate_handoff(self, target_agent: str, reason: HandoffReason, data: Dict[str, Any]) -> Dict[str, Any]:
        """Inizia il trasferimento del controllo verso l'agente di destinazione."""
        context = HandoffContext(
            from_agent=self.name,
            to_agent=target_agent,
            reason=reason,
            data=data,
            conversation_history=getattr(self.context, 'conversation_history', []),
            metadata={'timestamp': time.time(), 'initiator': self.name}
        )

        return self.orchestrator.execute_handoff(context)
```

---

## 2. Guardrails: Sicurezza e Controllo {#guardrails}

### Concetti Teorici

I **Guardrails** sono meccanismi di sicurezza che definiscono limiti operativi per gli agenti AI, garantendo comportamenti sicuri e conformi alle policy aziendali. Rappresentano il framework di **governance** dell'AI agentica.

#### Classificazione dei Guardrails

1. **Input Guardrails**: Validazione e sanitizzazione degli input utente
2. **Output Guardrails**: Controllo e filtraggio degli output dell'agente
3. **Behavioral Guardrails**: Controllo del comportamento durante l'esecuzione
4. **Resource Guardrails**: Limitazione dell'uso di risorse (API calls, tempo, memoria)
5. **Ethical Guardrails**: Conformità a principi etici e legali

#### Strategie di Implementazione

- **Rule-based**: Regole esplicite e deterministiche
- **ML-based**: Classificatori addestrati per rilevare contenuti problematici
- **Hybrid**: Combinazione di approcci rule-based e ML
- **Real-time**: Controlli durante l'esecuzione
- **Post-processing**: Validazione dell'output finale

### Implementazione Completa

```python
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re
import time
from enum import Enum

# Definiamo una classe GuardrailSeverity che eredita da Enum
# Enum è una classe speciale di Python che ci permette di definire un insieme fisso di costanti
# Queste costanti rappresentano i diversi livelli di severità per le violazioni dei guardrail
class GuardrailSeverity(Enum):
    """Livelli di severità per violazioni guardrail."""
    INFO = "info"           # Violazione informativa
    WARNING = "warning"     # Violazione di avvertimento
    ERROR = "error"         # Violazione di errore
    CRITICAL = "critical"   # Violazione critica

# Il decoratore @dataclass ci permette di creare una classe per contenere i dati delle violazioni del guardrail
# automatizzando la creazione di __init__, __repr__, __eq__ e altri metodi speciali
@dataclass
class GuardrailViolation:
    """Rappresenta una violazione di guardrail."""
    rule_name: str
    severity: GuardrailSeverity
    message: str
    context: Dict[str, Any]
    timestamp: float
    suggested_action: Optional[str] = None

# ABC (Abstract Base Class) è un modulo Python che fornisce il meccanismo per creare classi astratte
# Una classe astratta è una classe che non può essere istanziata direttamente ma serve come "template" per altre classi che la ereditano

# Quando una classe eredita da ABC:
# 1. Non può essere istanziata direttamente (non si può fare GuardrailRule())
# 2. Definisce un'interfaccia che le classi figlie DEVONO implementare
# 3. Garantisce che tutte le classi derivate abbiano una struttura comune
class GuardrailRule(ABC):
    """Classe base per regole di guardrail."""

    # Il costruttore inizializza gli attributi base comuni a tutte le regole
    def __init__(self, name: str, severity: GuardrailSeverity):
        self.name = name
        self.severity = severity

    # @abstractmethod indica che questo metodo DEVE essere implementato dalle classi figlie
    # Se una classe figlia non implementa validate(), Python darà errore quando si prova a istanziarla
    # Questo garantisce che tutte le regole di guardrail abbiano un metodo validate() funzionante
    @abstractmethod
    def validate(self, content: Any, context: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Valida il contenuto contro la regola."""
        pass

class ContentFilterRule(GuardrailRule):
    """Regola per filtraggio contenuti sensibili."""

    def __init__(self, forbidden_patterns: List[str], severity: GuardrailSeverity):
        # Chiamiamo il costruttore della classe padre (GuardrailRule) passando:
        # - "content_filter" come nome fisso della regola
        # - severity ricevuto come parametro che indica il livello di gravità della violazione
        super().__init__("content_filter", severity)

        # Creiamo una lista di pattern regex compilati partendo dalla lista di stringhe forbidden_patterns
        # Per ogni pattern nella lista:
        # - re.compile() compila il pattern in un oggetto regex per performance migliori
        # - re.IGNORECASE rende il matching case-insensitive
        # - il risultato è assegnato all'attributo self.forbidden_patterns
        self.forbidden_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in forbidden_patterns]

    # Implementa il metodo astratto validate() definito nella classe base GuardrailRule
    # Questo metodo controlla se il contenuto contiene pattern proibiti e restituisce una violazione se trovati
    # Args:
    #   content: Il contenuto da validare (deve essere una stringa)
    #   context: Dizionario con informazioni di contesto aggiuntive
    # Returns:
    #   GuardrailViolation se trova un pattern proibito, None altrimenti
    def validate(self, content: Any, context: Dict[str, Any]) -> Optional[GuardrailViolation]:
        if not isinstance(content, str):
            return None

        for pattern in self.forbidden_patterns:
            if pattern.search(content):
                return GuardrailViolation(
                    rule_name=self.name,
                    severity=self.severity,
                    message=f"Contenuto proibito rilevato: {pattern.pattern}",
                    context=context,
                    timestamp=time.time(),
                    suggested_action="Rimuovere o modificare il contenuto"
                )
        return None

class ResourceLimitRule(GuardrailRule):
    """Regola per limitazione uso risorse."""

    def __init__(self, max_api_calls: int, max_execution_time: float):
        # Inizializza la classe ResourceLimitRule chiamando il costruttore della classe padre GuardrailRule
        # con nome fisso "resource_limit" e severità ERROR. Questo guardrail serve a limitare l'uso delle risorse.
        # Parametri (argomenti):
        # - max_api_calls: numero massimo di chiamate API consentite
        # - max_execution_time: tempo massimo di esecuzione in secondi
        super().__init__("resource_limit", GuardrailSeverity.ERROR)
        self.max_api_calls = max_api_calls
        self.max_execution_time = max_execution_time

    def validate(self, content: Any, context: Dict[str, Any]) -> Optional[GuardrailViolation]:
        """Implementa il metodo validate() richiesto dalla classe base GuardrailRule.
        Controlla che l'utilizzo delle risorse rimanga entro i limiti configurati.

        Args:
            content: Il contenuto da validare (non utilizzato in questa regola)
            context: Dizionario con informazioni di contesto, deve contenere:
                - api_calls: numero di chiamate API effettuate
                - start_time: timestamp di inizio esecuzione

        Returns:
            GuardrailViolation se vengono superati i limiti di risorse configurati
            None se tutti i controlli passano
        """
        # Controlla numero di API calls
        if context.get('api_calls', 0) > self.max_api_calls:
            return GuardrailViolation(
                rule_name=self.name,
                severity=self.severity,
                message=f"Superato limite API calls: {context['api_calls']}/{self.max_api_calls}",
                context=context,
                timestamp=time.time(),
                suggested_action="Ridurre numero di chiamate API"
            )

        # Controlla tempo di esecuzione
        execution_time = time.time() - context.get('start_time', time.time())
        if execution_time > self.max_execution_time:
            return GuardrailViolation(
                rule_name=self.name,
                severity=self.severity,
                message=f"Superato limite tempo esecuzione: {execution_time:.2f}s/{self.max_execution_time}s",
                context=context,
                timestamp=time.time(),
                suggested_action="Ottimizzare performance o aumentare timeout"
            )

        return None

# Questa classe implementa il motore di gestione dei guardrails che permette di:
# - Definire e applicare regole di validazione per input, output e comportamento
# - Tracciare e loggare le violazioni delle regole
# - Generare report sulle violazioni rilevate
class GuardrailEngine:
    """Motore per gestione e applicazione guardrails."""

    # Il costruttore inizializza le strutture dati vuote che verranno popolate tramite i metodi dedicati:
    # - input_rules: lista delle regole di validazione per gli input
    # - output_rules: lista delle regole di validazione per gli output
    # - behavioral_rules: lista delle regole di validazione comportamentali
    # - violations_log: registro storico delle violazioni rilevate
    def __init__(self):
        self.input_rules: List[GuardrailRule] = []
        self.output_rules: List[GuardrailRule] = []
        self.behavioral_rules: List[GuardrailRule] = []
        self.violations_log: List[GuardrailViolation] = []

    def add_input_rule(self, rule: GuardrailRule):
        """Aggiunge regola per input."""
        self.input_rules.append(rule)

    def add_output_rule(self, rule: GuardrailRule):
        """Aggiunge regola per output."""
        self.output_rules.append(rule)

    def add_behavioral_rule(self, rule: GuardrailRule):
        """Aggiunge regola comportamentale."""
        self.behavioral_rules.append(rule)

    def validate_input(self, input_data: Any, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Valida input dell'utente."""
        return self._apply_rules(self.input_rules, input_data, context)

    def validate_output(self, output_data: Any, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Valida output dell'agente."""
        return self._apply_rules(self.output_rules, output_data, context)

    def validate_behavior(self, behavior_data: Any, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Valida comportamento durante esecuzione."""
        return self._apply_rules(self.behavioral_rules, behavior_data, context)

    def _apply_rules(self, rules: List[GuardrailRule], data: Any, context: Dict[str, Any]) -> List[GuardrailViolation]:
        """Applica set di regole ai dati."""
        violations = []

        for rule in rules:
            # Il metodo .validate() controlla se i dati rispettano la regola del guardrail.
            # Si tratta del metodo obbligatorio definito con il decoratore @abstactmethod nella classe base
            # Riceve in input i dati da validare e il contesto di esecuzione (data e context)
            # Restituisce un oggetto GuardrailViolation se la regola è violata, altrimenti None
            violation = rule.validate(data, context)
            if violation:
                violations.append(violation)
                self.violations_log.append(violation)

        return violations

    def get_violation_summary(self) -> Dict[str, Any]:
        """Restituisce sommario delle violazioni."""
        severity_counts = {}
        rule_counts = {}

        for violation in self.violations_log:
            severity_counts[violation.severity.value] = severity_counts.get(violation.severity.value, 0) + 1
            rule_counts[violation.rule_name] = rule_counts.get(violation.rule_name, 0) + 1

        return {
            'total_violations': len(self.violations_log),
            'by_severity': severity_counts,
            'by_rule': rule_counts,
            'recent_violations': self.violations_log[-10:]  # Ultime 10
        }
```

---

## 3. Structured Tools con Pydantic {#structured-tools}

### Concetti Teorici

Gli **Structured Tools** rappresentano l'evoluzione dei tool tradizionali, utilizzando **Pydantic** per definire schemi rigorosi di input e output. Questo approccio garantisce:

- **Type Safety**: Validazione automatica dei tipi a runtime
- **Data Validation**: Controllo della validità e coerenza dei dati
- **Auto-documentation**: Generazione automatica di documentazione
- **IDE Support**: Autocompletamento e controllo errori nell'IDE
- **Serialization**: Conversione automatica JSON ↔ Python objects

#### Vantaggi del Paradigma Structured

1. **Prevenzione Errori**: Catch degli errori di tipo prima dell'esecuzione
2. **Contract Definition**: Definizione chiara di interfacce tra componenti
3. **Enhanced LLM Communication**: Schema più ricchi per migliore comprensione LLM
4. **Maintainability**: Codice più facile da mantenere e debuggare

### Implementazione Avanzata

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Any, Optional, Union, Literal
from datetime import datetime
from enum import Enum

# Definizione di modelli Pydantic per structured input/output
# La classe eredita sia da str che da Enum per:
# 1. Avere tutti i metodi e le funzionalità delle stringhe (str)
# 2. Mantenere la funzionalità di enumerazione (Enum)
# 3. Permettere la serializzazione diretta in JSON senza conversioni
# 4. Consentire il confronto diretto con stringhe normali
# Questo approccio è molto utile quando si lavora con API e serializzazione di dati
class TaskPriority(str, Enum):
    """Enumerazione per priorità task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    """Enumerazione per status task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Definiamo una classe TaskInput che eredita dalla classe BaseModel di Pydantic
# BaseModel è la classe base di Pydantic che fornisce:
# 1. Validazione automatica dei tipi di dati
# 2. Serializzazione/deserializzazione JSON
# 3. Generazione automatica di documentazione
# 4. Controllo dei valori ammessi per ogni campo
# 5. Conversione automatica tra tipi di dati compatibili
class TaskInput(BaseModel):
    """Schema strutturato per input di un task."""
    title: str = Field(..., min_length=1, max_length=200, description="Titolo del task")
    description: Optional[str] = Field(None, max_length=1000, description="Descrizione dettagliata")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Priorità del task")
    due_date: Optional[datetime] = Field(None, description="Data di scadenza")
    tags: List[str] = Field(default_factory=list, description="Tag per categorizzazione")
    estimated_hours: Optional[float] = Field(None, gt=0, le=1000, description="Ore stimate")

    # Il decoratore @validator di Pydantic permette di definire funzioni di validazione personalizzate per specifici campi
    # In questo caso valida il campo 'tags' sta verificando:
    # 1. Che non ci siano più di 10 tag
    # 2. Normalizza i tag rimuovendo spazi e convertendo in minuscolo
    # Il primo parametro 'cls' è la classe stessa, 'v' è il valore del campo da validare
    @validator('tags')
    def validate_tags(cls, v):
        """Valida e normalizza i tag."""
        if len(v) > 10:
            raise ValueError("Massimo 10 tag consentiti")
        return [tag.lower().strip() for tag in v if tag.strip()]

    # @root_validator è un decoratore di Pydantic che permette di validare più campi contemporaneamente
    # A differenza di @validator che valida un singolo campo, @root_validator ha accesso a tutti i valori
    # del modello attraverso il dizionario 'values'

    # Il decoratore viene chiamato dopo che tutti i singoli validatori (@validator) sono stati eseguiti
    # Questo lo rende ideale per validazioni che coinvolgono relazioni tra campi diversi

    # In questo caso specifico:
    # 1. Riceve il dizionario 'values' con tutti i campi del modello
    # 2. Estrae il campo 'due_date' usando il metodo get() che restituisce None se il campo non esiste
    # 3. Controlla che la data sia nel futuro confrontandola con datetime.now()
    # 4. Se la validazione fallisce solleva un ValueError
    # 5. Deve sempre restituire il dizionario values alla fine
    @root_validator
    def validate_due_date(cls, values):
        """Valida che la due date sia futura."""
        due_date = values.get('due_date')
        if due_date and due_date < datetime.now():
            raise ValueError("Due date deve essere nel futuro")
        return values

class TaskOutput(BaseModel):
    """Schema strutturato per output di task completion."""
    # ... in Field indica che il campo è obbligatorio e non ha un valore di default
    # Quando si usa ... il campo DEVE essere specificato alla creazione dell'oggetto
    # altrimenti Pydantic solleverà un ValidationError
    task_id: str = Field(..., description="Identificatore univoco del task")
    status: TaskStatus = Field(..., description="Status finale del task")

    # Qui invece None è il valore di default, quindi il campo è opzionale
    result: Optional[Dict[str, Any]] = Field(None, description="Risultato dell'esecuzione")

    # Altro esempio di campo obbligatorio con ...
    execution_time: float = Field(..., ge=0, description="Tempo di esecuzione in secondi")
    error_message: Optional[str] = Field(None, description="Messaggio di errore se applicabile")
    resources_used: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Risorse utilizzate")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp completamento")

class StructuredTaskTool:
    """Tool strutturato con validazione Pydantic completa."""

    def __init__(self, name: str):
        self.name = name
        self.executions: List[TaskOutput] = []

    # Questo metodo esegue un task prendendo in input un TaskInput validato da Pydantic
    # e restituendo un TaskOutput strutturato. In particolare:
    # 1. Registra il tempo di inizio esecuzione
    # 2. Genera un ID univoco per il task usando timestamp e hash del titolo
    # 3. Processa il task tramite _process_task() in un blocco try/except
    # 4. Traccia le risorse utilizzate (tempo CPU, memoria, chiamate API)
    # 5. Restituisce un TaskOutput con tutti i dettagli dell'esecuzione
    # NOTA: Il simbolo -> dopo la definizione del metodo indica il tipo di ritorno atteso,
    # in questo caso TaskOutput specifica che il metodo restituirà un oggetto di tipo TaskOutput
    def execute_task(self, task_input: TaskInput) -> TaskOutput:
        """Esegue task con input/output strutturati."""
        start_time = time.time()
        task_id = f"task_{int(time.time())}_{hash(task_input.title)}"

        try:
            # Simula elaborazione del task
            result = self._process_task(task_input)

            execution_time = time.time() - start_time

            output = TaskOutput(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                resources_used={
                    'cpu_time': execution_time,
                    'memory_mb': 50,  # Simulato
                    'api_calls': result.get('api_calls_made', 0)
                }
            )

        except Exception as e:
            output = TaskOutput(
                task_id=task_id,
                status=TaskStatus.FAILED,
                execution_time=time.time() - start_time,
                error_message=str(e),
                resources_used={'cpu_time': time.time() - start_time}
            )

        self.executions.append(output)
        return output

    def _process_task(self, task_input: TaskInput) -> Dict[str, Any]:
        """Logica di elaborazione del task."""
        # Simula elaborazione basata sulla priorità
        processing_time = {
            TaskPriority.LOW: 0.5,
            TaskPriority.MEDIUM: 1.0,
            TaskPriority.HIGH: 1.5,
            TaskPriority.CRITICAL: 0.1  # Processamento immediato
        }

        time.sleep(processing_time[task_input.priority])

        return {
            'processed_title': task_input.title.upper(),
            'estimated_completion': datetime.now() + timedelta(hours=task_input.estimated_hours or 1),
            'categorization': self._categorize_task(task_input),
            'api_calls_made': len(task_input.tags)  # Simula API calls per tag processing
        }

    def _categorize_task(self, task_input: TaskInput) -> str:
        """Categorizza il task basandosi sui contenuti."""
        if any(word in task_input.title.lower() for word in ['analisi', 'report', 'dati']):
            return 'analytics'
        elif any(word in task_input.title.lower() for word in ['codice', 'sviluppo', 'bug']):
            return 'development'
        else:
            return 'general'

    def get_execution_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche delle esecuzioni."""
        if not self.executions:
            return {'total_executions': 0}

        # Compone la lista dei task eseguiti
        completed = [ex for ex in self.executions if ex.status == TaskStatus.COMPLETED]
        # Compone la lista dei task falliti
        failed = [ex for ex in self.executions if ex.status == TaskStatus.FAILED]

        # Calcola la media di esecuzione dei task
        avg_execution_time = sum(ex.execution_time for ex in self.executions) / len(self.executions)

        return {
            'total_executions': len(self.executions),
            'completed': len(completed),
            'failed': len(failed),
            'success_rate': len(completed) / len(self.executions) * 100,
            'avg_execution_time': avg_execution_time,
            'total_cpu_time': sum(ex.resources_used.get('cpu_time', 0) for ex in self.executions)
        }
```

---

## 4. Schema Pydantic per Output Strutturati {#pydantic-schemas}

### Concetti Teorici

Gli **Schema Pydantic** definiscono contratti rigorosi per l'output degli agenti, garantendo consistenza e validità dei risultati. Questo approccio è fondamentale per:

- **Predictable Outputs**: Output sempre conformi allo schema definito
- **Downstream Integration**: Facilita integrazione con altri sistemi
- **Quality Assurance**: Validazione automatica della qualità dell'output
- **Documentation**: Schema auto-documentanti per API e interfacce

#### Pattern di Design per Schemi

1. **Composition**: Schemi complessi composti da schemi più semplici
2. **Inheritance**: Gerarchia di schemi con specializzazione
3. **Union Types**: Gestione di output multipli possibili
4. **Dynamic Schemas**: Schemi che si adattano al contesto

### Implementazione Completa

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Any, Optional, Union, Generic, TypeVar
from datetime import datetime
from decimal import Decimal
import json

# TypeVar è un costruttore che crea una variabile di tipo generica.
# T è una variabile di tipo che può essere usata per creare classi e funzioni generiche.
# Quando si usa T come parametro di tipo, Python permette di specificare il tipo concreto
# al momento della creazione dell'istanza o della chiamata della funzione.
# Ad esempio: List[T] può diventare List[str] o List[int] a seconda del contesto.
T = TypeVar('T')

class BaseAgentOutput(BaseModel):
    """
    Schema base per tutti gli output degli agenti.

    Questa classe definisce la struttura base che tutti gli output degli agenti devono seguire.
    Eredita da BaseModel di Pydantic per la validazione automatica dei dati.

    Attributi:
        agent_name (str): Nome identificativo dell'agente che ha generato l'output
        timestamp (datetime): Data e ora di generazione dell'output, default al momento attuale
        execution_id (str): Identificatore univoco per tracciare l'esecuzione specifica
        metadata (Dict[str, Any]): Dizionario per dati aggiuntivi flessibili, default vuoto
    """
    agent_name: str = Field(..., description="Nome dell'agente che ha generato l'output")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp generazione")
    execution_id: str = Field(..., description="ID univoco dell'esecuzione")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata aggiuntivi")

    # La classe Config è una classe speciale di Pydantic che permette di configurare
    # il comportamento della serializzazione del modello.
    # In questo caso, definiamo come devono essere codificati alcuni tipi speciali
    # quando il modello viene convertito in JSON:
    # 1. Per il tipo datetime, usiamo il metodo isoformat() per convertirlo in stringa ISO 8601
    # 2. Per il tipo Decimal, lo convertiamo in stringa per mantenere la precisione
    # Questo è necessario perché JSON non supporta nativamente questi tipi di dati
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # Converte datetime in formato ISO
            Decimal: lambda v: str(v)           # Converte Decimal in stringa
        }

class AnalysisResult(BaseModel):
    """Schema per risultati di analisi dati."""
    summary: str = Field(..., min_length=10, description="Riassunto dell'analisi")
    key_insights: List[str] = Field(..., min_items=1, description="Insight principali")
    metrics: Dict[str, Union[int, float, str]] = Field(..., description="Metriche calcolate")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Livello di confidenza")
    recommendations: List[str] = Field(default_factory=list, description="Raccomandazioni")

    # Si tratta di un metodo obbligatorio che deve sempre essere presvisto per evitare errori
    # Il validatore controlla che:
    # 1. Non ci siano più di 10 insight nella lista
    # 2. Rimuove gli spazi bianchi all'inizio e alla fine di ogni insight
    # 3. Filtra eventuali insight vuoti dalla lista
    # 4. Restituisce la lista pulita e validata
    # Questo garantisce che i dati siano sempre consistenti e ben formattati
    @validator('key_insights')
    def validate_insights(cls, v):
        if len(v) > 10:
            raise ValueError("Massimo 10 insight consentiti")
        return [insight.strip() for insight in v if insight.strip()]

# Questa classe eredita da BaseAgentOutput che fornisce gli attributi base
# come agent_name, timestamp, execution_id e metadata necessari per tracciare
# e identificare ogni output generato dagli agenti nel sistema
class DocumentProcessingOutput(BaseAgentOutput):
    """Schema specializzato per elaborazione documenti."""
    document_type: str = Field(..., description="Tipo di documento processato")
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict, description="Entità estratte")
    sentiment_analysis: Optional[Dict[str, float]] = Field(None, description="Analisi sentiment")
    key_topics: List[str] = Field(default_factory=list, description="Topic principali")
    processing_stats: Dict[str, Union[int, float]] = Field(..., description="Statistiche elaborazione")
    analysis_result: AnalysisResult = Field(..., description="Risultato dell'analisi")

    @validator('document_type')
    def validate_document_type(cls, v):
        allowed_types = ['pdf', 'docx', 'txt', 'html', 'markdown']
        if v.lower() not in allowed_types:
            raise ValueError(f"Tipo documento non supportato: {v}")
        return v.lower()

# Questa classe gestisce gli output di un workflow multi-agente, tracciando l'esecuzione
# e i risultati di ogni agente coinvolto nel processo. Implementa validazioni per garantire
# la consistenza dei dati e la corretta sequenza di handoff tra gli agenti.
class MultiAgentWorkflowOutput(BaseModel):
    """Schema per output di workflow multi-agente."""
    workflow_id: str = Field(..., description="ID del workflow")
    total_execution_time: float = Field(..., ge=0, description="Tempo totale di esecuzione")
    agent_outputs: List[BaseAgentOutput] = Field(..., description="Output di tutti gli agenti")
    final_result: Dict[str, Any] = Field(..., description="Risultato finale consolidato")
    handoff_chain: List[str] = Field(..., description="Catena di handoff tra agenti")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Tasso di successo")

    @validator('agent_outputs')
    def validate_agent_outputs(cls, v):
        if not v:
            raise ValueError("Deve contenere almeno un output di agente")
        return v

    # Questo metodo verifica tutti i valori del modello per garantire la consistenza tra gli agenti
    # nella catena di handoff e i loro output. In particolare:
    # 1. Estrae la lista degli handoff e degli output degli agenti
    # 2. Crea due insiemi: uno con i nomi degli agenti che hanno generato output e uno con gli agenti nella catena di handoff
    # 3. Verifica che tutti gli agenti nella catena di handoff abbiano effettivamente prodotto un output (usando issubset)
    # 4. Se la verifica fallisce solleva un errore, altrimenti restituisce i valori validati
    @root_validator
    def validate_consistency(cls, values):
        """Valida consistenza tra handoff_chain e agent_outputs."""
        handoff_chain = values.get('handoff_chain', [])
        agent_outputs = values.get('agent_outputs', [])

        output_agents = {output.agent_name for output in agent_outputs}
        # Converte la lista handoff_chain in un set (insieme) per rimuovere eventuali duplicati
        # e permettere operazioni efficienti di confronto come issubset()
        chain_agents = set(handoff_chain)

        if not chain_agents.issubset(output_agents):
            raise ValueError("Tutti gli agenti nella handoff chain devono avere un output")

        return values

# Factory per creazione dinamica di schemi
class SchemaFactory:
    """Factory per creazione dinamica di schemi Pydantic."""

    # @staticmethod è un decoratore che indica che il metodo non richiede l'accesso
    # all'istanza (self) o alla classe (cls). È un metodo che appartiene alla classe
    # ma si comporta come una funzione normale, senza accesso allo stato dell'oggetto.
    # Viene usato quando la logica del metodo è correlata alla classe ma non necessita
    # di accedere ai suoi attributi o metodi.
    @staticmethod
    def create_response_schema(agent_type: str, fields_definition: Dict[str, Any]) -> type:
        """Crea dinamicamente schema di risposta per tipo di agente."""

        # Campi base sempre presenti
        base_fields = {
            'agent_type': (str, Field(default=agent_type, description=f"Tipo agente: {agent_type}")),
            'status': (str, Field(..., description="Status dell'operazione")),
            'message': (Optional[str], Field(None, description="Messaggio descrittivo"))
        }

        # Unisce campi base con campi personalizzati
        # I doppi asterischi ** sono l'operatore di unpacking dei dizionari
        # Permettono di unire due dizionari in uno nuovo, espandendo tutti i loro elementi
        # {**dict1, **dict2} crea un nuovo dizionario con le chiavi/valori di entrambi
        all_fields = {**base_fields, **fields_definition}

        # Crea classe dinamicamente
        # La virgola dopo BaseAgentOutput è necessaria perché type() si aspetta una tupla di classi base
        # Anche con una sola classe base, la sintassi richiede una tupla, quindi la virgola la rende una tupla di un elemento
        return type(
            f"{agent_type.title()}Response",
            (BaseAgentOutput,),  # La virgola crea una tupla con un solo elemento
            {
                # __annotations__ è un dizionario speciale che contiene i tipi delle annotazioni
                # Viene creato con una dict comprehension che itera su all_fields
                # Per ogni coppia name:(field_type,field_def) in all_fields
                # Crea una entry name:field_type nel dizionario __annotations__
                # Es: 'status': str, 'message': Optional[str], etc.
                '__annotations__': {name: field_type for name, (field_type, _) in all_fields.items()},

                # Questo secondo dizionario contiene le definizioni dei campi (Field objects)
                # Viene creato con dict comprehension e unpacking (**)
                # Per ogni coppia name:(field_type,field_def) in all_fields
                # Crea una entry name:field_def nel dizionario
                # Es: 'status': Field(...), 'message': Field(None), etc.
                # L'operatore ** espande il dizionario inline
                **{name: field_def for name, (_, field_def) in all_fields.items()}
            }
        )

# Esempio di utilizzo del factory
def create_specialized_schemas():
    """Esempi di creazione schemi specializzati."""

    # Schema per agente di trading
    # create_response_schema crea uno schema Pydantic personalizzato per le risposte dell'agente
    # Prende come parametri:
    # - agent_type: stringa che identifica il tipo di agente (es. "trading")
    # - fields_definition: dizionario che definisce i campi specifici dello schema
    #
    # Ogni campo è definito come tupla (tipo, Field(...)) dove:
    # - tipo è il tipo Python del campo (int, str, etc)
    # - Field(...) è un oggetto Pydantic che definisce validazioni e metadati
    #
    # Lo schema risultante avrà:
    # 1. Campi base comuni a tutti gli agenti (agent_type, status, message)
    # 2. Campi specifici definiti in fields_definition
    # 3. Validazione automatica dei tipi e constraints
    TradingAgentResponse = SchemaFactory.create_response_schema(
        agent_type="trading",
        fields_definition={
            'trades_executed': (int, Field(..., ge=0, description="Numero di trade eseguiti")),
            'total_profit': (Decimal, Field(..., description="Profitto totale")),
            'risk_metrics': (Dict[str, float], Field(..., description="Metriche di rischio")),
            'market_analysis': (str, Field(..., min_length=50, description="Analisi di mercato"))
        }
    )

    # Schema per agente di supporto clienti
    SupportAgentResponse = SchemaFactory.create_response_schema(
        agent_type="support",
        fields_definition={
            'ticket_id': (str, Field(..., description="ID del ticket")),
            'resolution_status': (str, Field(..., description="Status di risoluzione")),
            'customer_satisfaction': (Optional[float], Field(None, ge=1.0, le=5.0, description="Soddisfazione cliente")),
            'follow_up_required': (bool, Field(..., description="Richiede follow-up"))
        }
    )

    return TradingAgentResponse, SupportAgentResponse
```

---

## 5. Multi-Agent Orchestration {#multi-agent-orchestration}

### Concetti Teorici

L'**orchestrazione multi-agente** è l'arte di coordinare diversi agenti AI per lavorare insieme verso obiettivi comuni. Questo paradigma si basa sui principi di:

#### Architetture di Orchestrazione

1. **Centralized Orchestration**: Un supervisore centrale coordina tutti gli agenti
2. **Decentralized Coordination**: Agenti si coordinano direttamente tra loro
3. **Hierarchical Structure**: Struttura gerarchica con livelli di supervisione
4. **Event-Driven Architecture**: Coordinazione basata su eventi e messaggi

#### Pattern di Comunicazione

- **Synchronous**: Comunicazione bloccante con risposta immediata
- **Asynchronous**: Comunicazione non-bloccante con callback
- **Publish-Subscribe**: Pattern di messaggistica disaccoppiata
- **Request-Response**: Pattern classico di richiesta/risposta

---

## 6. Chain of Thought e Reasoning Patterns {#chain-of-thought}

### Concetti Teorici

Il **Chain of Thought (CoT)** è una tecnica che consente agli LLM di esplicitare il proprio processo di ragionamento, migliorando significativamente la qualità delle risposte per problemi complessi.

#### Tipologie di Chain of Thought

1. **Zero-shot CoT**: "Ragioniamo passo dopo passo" senza esempi
2. **Few-shot CoT**: Esempi di ragionamento nel prompt
3. **Auto-CoT**: Generazione automatica di esempi di ragionamento
4. **Tree of Thoughts**: Esplorazione di multipli percorsi di ragionamento

#### Vantaggi del Reasoning Esplicito

- **Interpretabilità**: Comprensione del processo decisionale
- **Debugging**: Identificazione di errori nel ragionamento
- **Trust**: Maggiore fiducia nelle decisioni dell'agente
- **Learning**: Miglioramento continuo attraverso feedback

### Implementazione

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

# Questa classe eredita da Pydantic BaseModel e definisce un singolo step del ragionamento
# Ogni step contiene:
# - Un numero progressivo che identifica la posizione nella sequenza
# - Una descrizione testuale dello step
# - Il ragionamento dettagliato applicato
# - Un eventuale risultato intermedio (opzionale)
# - Un valore di confidenza tra 0 e 1 che indica quanto l'agente è sicuro del passo
class ReasoningStep(BaseModel):
    """Singolo step del processo di ragionamento."""
    step_number: int = Field(..., description="Numero del passo")
    description: str = Field(..., description="Descrizione dello step")
    reasoning: str = Field(..., description="Ragionamento applicato")
    intermediate_result: Any = Field(None, description="Risultato intermedio")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidenza nel passo")

# Questa classe eredita da Pydantic BaseModel e definisce l'intera sequenza di passi del ragionamento.
# Contiene:
# - Il problema originale da risolvere
# - La lista degli step di ragionamento con il loro dettaglio
# - La risposta finale calcolata
# - Un valore di confidenza complessivo sul risultato
# - Eventuali approcci alternativi considerati ma non utilizzati
class ChainOfThoughtResult(BaseModel):
    """Risultato completo del Chain of Thought."""
    problem_statement: str = Field(..., description="Problema originale")
    reasoning_steps: List[ReasoningStep] = Field(..., description="Steps di ragionamento")
    final_answer: Any = Field(..., description="Risposta finale")
    overall_confidence: float = Field(..., description="Confidenza complessiva")
    alternative_approaches: List[str] = Field(default_factory=list, description="Approcci alternativi")

    @validator('reasoning_steps')
    def validate_steps(cls, v):
        if len(v) < 1:
            raise ValueError("Deve contenere almeno un step di ragionamento")
        return v

class ReasoningEngine:
    """Motore per gestione del Chain of Thought."""

    def __init__(self, llm_client):
        self.llm = llm_client
        self.cot_prompt_template = """
        Problema: {problem}

        Risolvi questo problema seguendo questi passi:
        1. Analizza il problema e identifica i componenti chiave
        2. Considera possibili approcci di soluzione
        3. Scegli l'approccio migliore e giustifica la scelta
        4. Esegui la soluzione passo dopo passo
        5. Verifica il risultato e considera alternative

        Per ogni passo, spiega chiaramente il tuo ragionamento.
        """

    def solve_with_cot(self, problem: str, context: Dict[str, Any] = None) -> ChainOfThoughtResult:
        """Risolve problema usando Chain of Thought."""

        # Prepara prompt con contesto
        # .format() sostituisce i placeholder nel template (es. {problem}) con i valori forniti
        prompt = self.cot_prompt_template.format(problem=problem)
        if context:
            # .dumps() converte un oggetto Python in una stringa JSON formattata
            # indent=2 aggiunge indentazione per rendere il JSON più leggibile
            prompt += f"\nContesto aggiuntivo: {json.dumps(context, indent=2)}"

        # Genera ragionamento
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un esperto problem solver. Ragiona sempre passo dopo passo."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        reasoning_text = response.choices[0].message.content

        # Estrae steps di ragionamento
        steps = self._extract_reasoning_steps(reasoning_text)
        final_answer = self._extract_final_answer(reasoning_text)

        return ChainOfThoughtResult(
            problem_statement=problem,
            reasoning_steps=steps,
            final_answer=final_answer,
            overall_confidence=self._calculate_overall_confidence(steps),
            alternative_approaches=self._extract_alternatives(reasoning_text)
        )

    # Questo metodo analizza il testo di risposta dell'LLM ed estrae gli step del ragionamento
    # utilizzando parole chiave come 'passo', 'step', 'primo', 'secondo', 'quindi'.
    # Per ogni step trovato crea un oggetto ReasoningStep con:
    # - Numero progressivo dello step
    # - Descrizione generica (es. "Step 1")
    # - Il testo completo del ragionamento
    # - Un valore di confidenza (attualmente fisso a 0.8)
    # Limita il risultato a massimo 10 step per evitare ragionamenti troppo lunghi
    def _extract_reasoning_steps(self, text: str) -> List[ReasoningStep]:
        """Estrae steps di ragionamento dal testo."""
        # Implementazione semplificata - in pratica si userebbe NLP più sofisticato
        lines = text.split('\n')
        steps = []
        current_step = 1

        for line in lines:
            if line.strip() and any(word in line.lower() for word in ['passo', 'step', 'primo', 'secondo', 'quindi']):
                steps.append(ReasoningStep(
                    step_number=current_step,
                    description=f"Step {current_step}",
                    reasoning=line.strip(),
                    confidence=0.8  # Placeholder
                ))
                current_step += 1

        return steps[:10]  # Massimo 10 steps

    def _extract_final_answer(self, text: str) -> str:
        """Estrae risposta finale dal ragionamento."""
        lines = text.split('\n')
        for line in reversed(lines):
            if line.strip() and any(word in line.lower() for word in ['risposta', 'soluzione', 'conclusione']):
                return line.strip()
        return "Risposta non trovata nel ragionamento"

    def _calculate_overall_confidence(self, steps: List[ReasoningStep]) -> float:
        """Calcola confidenza complessiva."""
        if not steps:
            return 0.0
        return sum(step.confidence for step in steps) / len(steps)

    def _extract_alternatives(self, text: str) -> List[str]:
        """Estrae approcci alternativi menzionati."""
        # Implementazione semplificata
        alternatives = []
        if 'alternativ' in text.lower():
            alternatives.append("Approccio alternativo menzionato nel ragionamento")
        return alternatives
```

---

## 7. Context Management e Memory Systems {#context-management}

### Concetti Teorici

Il **Context Management** è fondamentale per mantenere coerenza e continuità nelle interazioni multi-turno. I sistemi di memoria permettono agli agenti di:

- **Mantenere Stato**: Ricordare informazioni tra interazioni
- **Apprendere Progressivamente**: Migliorare basandosi su esperienze passate
- **Personalizzare Risposte**: Adattare comportamento al contesto specifico
- **Gestire Sessioni Lunghe**: Mantenere performance anche con conversazioni estese

#### Tipologie di Memoria

1. **Working Memory**: Memoria a breve termine per il task corrente
2. **Episodic Memory**: Memoria di eventi e interazioni specifiche
3. **Semantic Memory**: Conoscenza strutturata e fatti appresi
4. **Procedural Memory**: Competenze e procedure apprese

### Implementazione

```python
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
from collections import deque
import hashlib

# Il decoratore @dataclass di Python semplifica la definizione di classi per la gestione dei dati
# automatizzando la creazione di __init__, __repr__ e altri metodi speciali
@dataclass
class MemoryEntry:
    """Singola entry nella memoria."""
    id: str
    content: Dict[str, Any]
    timestamp: datetime
    memory_type: str
    importance_score: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

class ContextWindow:
    """Finestra di contesto con gestione automatica della dimensione."""

    def __init__(self, max_tokens: int = 4000, overlap_tokens: int = 200):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.current_content: deque = deque(maxlen=100)
        self.token_count = 0

    # Questo metodo gestisce l'aggiunta di contenuto alla finestra di contesto
    # Stima il numero di token del nuovo contenuto moltiplicando il numero di parole per 1.3
    # Verifica se il contenuto supera la dimensione massima della finestra
    # Rimuove contenuti vecchi se necessario per fare spazio al nuovo contenuto
    # Crea una nuova entry con contenuto, tipo, timestamp e stima dei token
    # Aggiunge l'entry alla finestra e aggiorna il conteggio totale dei token
    # Restituisce True se l'aggiunta è avvenuta con successo, False altrimenti
    def add_content(self, content: str, content_type: str = "message") -> bool:
        """Aggiunge contenuto alla finestra di contesto."""
        estimated_tokens = len(content.split()) * 1.3  # Stima approssimativa

        # Se il contenuto supera la finestra, tronca o rifiuta
        if estimated_tokens > self.max_tokens:
            return False

        # Rimuovi contenuto vecchio se necessario
        while self.token_count + estimated_tokens > self.max_tokens and self.current_content:
            removed = self.current_content.popleft()
            self.token_count -= removed['estimated_tokens']

        # Aggiungi nuovo contenuto
        entry = {
            'content': content,
            'type': content_type,
            'timestamp': datetime.now(),
            'estimated_tokens': estimated_tokens
        }

        self.current_content.append(entry)
        self.token_count += estimated_tokens

        return True

    def get_context_string(self) -> str:
        """Restituisce il contesto come stringa."""
        return "\n".join([entry['content'] for entry in self.current_content])

    # Questo metodo restituisce un dizionario con un riepilogo dello stato attuale della finestra di contesto
    # Include il numero totale di entry, il conteggio stimato dei token, la percentuale di utilizzo della finestra
    # e i timestamp della entry più vecchia e più recente. Utile per monitorare lo stato e l'utilizzo della finestra.
    def get_summary(self) -> Dict[str, Any]:
        """Restituisce summary della finestra di contesto."""
        return {
            'total_entries': len(self.current_content),
            'estimated_tokens': self.token_count,
            'utilization_percent': (self.token_count / self.max_tokens) * 100,
            'oldest_entry': self.current_content[0]['timestamp'] if self.current_content else None,
            'newest_entry': self.current_content[-1]['timestamp'] if self.current_content else None
        }

# Questa classe implementa un sistema di memoria persistente per agenti AI
# Utilizza SQLite per memorizzare le informazioni in modo permanente su disco
# Ogni agente ha un proprio ID univoco e può salvare/recuperare memorie
# Le memorie hanno metadati come tipo, importanza, timestamp e tag
# Il sistema mantiene anche una finestra di contesto come memoria di lavoro
class PersistentMemorySystem:
    """Sistema di memoria persistente per gli agenti"""
    def __init__(self, agent_id: str, db_path: str = "agent_memory.db"):
        self.agent_id = agent_id
        self.db_path = db_path
        self.working_memory = ContextWindow()
        self._init_database()

    def _init_database(self):
        """Inizializza database SQLite per memoria persistente."""
        conn = sqlite3.connect(self.db_path) # in un contesto reale andrebbe fornito l'indirizzo corretto del DB
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                content TEXT,
                memory_type TEXT,
                importance_score REAL,
                timestamp DATETIME,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME,
                tags TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def store_memory(self, content: Dict[str, Any], memory_type: str, importance_score: float, tags: List[str] = None) -> str:
        """Memorizza informazione nella memoria permanente."""

        # Genera un ID univoco per la memoria usando MD5 che crea un hash di 32 caratteri
        # dall'input combinando agent_id, contenuto e timestamp. Non usare per sicurezza.
        memory_id = hashlib.md5(
            f"{self.agent_id}_{json.dumps(content, sort_keys=True)}_{datetime.now()}".encode()
        ).hexdigest()

        entry = MemoryEntry(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            memory_type=memory_type,
            importance_score=importance_score,
            tags=tags or []
        )

        conn = sqlite3.connect(self.db_path)
        # Crea un cursore, ovvero un oggetto che permette di eseguire query SQL e
        # iterare sui risultati, fungendo da puntatore alla posizione corrente nel set di risultati
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO memories
            (id, agent_id, content, memory_type, importance_score, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.id, self.agent_id, json.dumps(entry.content),
            entry.memory_type, entry.importance_score, entry.timestamp,
            json.dumps(entry.tags)
        ))

        conn.commit()
        conn.close()

        return memory_id

    def retrieve_memories(self, query: str = None, memory_type: str = None,
                         limit: int = 10, min_importance: float = 0.0) -> List[MemoryEntry]:
        """Recupera memorie basandosi sui criteri."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = "SELECT * FROM memories WHERE agent_id = ? AND importance_score >= ?"
        params = [self.agent_id, min_importance]

        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)

        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        memories = []
        for row in rows:
            memories.append(MemoryEntry(
                id=row[0],
                content=json.loads(row[2]),
                timestamp=datetime.fromisoformat(row[5]),
                memory_type=row[3],
                importance_score=row[4],
                access_count=row[6],
                last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
                tags=json.loads(row[8]) if row[8] else []
            ))

        # Aggiorna contatori di accesso
        for memory in memories:
            self._update_access_count(memory.id)

        conn.close()
        return memories

    def _update_access_count(self, memory_id: str):
        """Aggiorna contatore di accesso per una memoria."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE memories
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        ''', (datetime.now(), memory_id))

        conn.commit()
        conn.close()

    def consolidate_memories(self, consolidation_threshold: int = 5):
        """Consolida memorie frequentemente accedute aumentandone l'importanza."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE memories
            SET importance_score = CASE
                WHEN access_count >= ? THEN LEAST(importance_score * 1.1, 1.0)
                ELSE importance_score
            END
            WHERE agent_id = ?
        ''', (consolidation_threshold, self.agent_id))

        conn.commit()
        conn.close()

    def cleanup_old_memories(self, retention_days: int = 30, min_importance: float = 0.3):
        """Rimuove memorie vecchie e poco importanti."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM memories
            WHERE agent_id = ? AND timestamp < ? AND importance_score < ?
        ''', (self.agent_id, cutoff_date, min_importance))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count
```

---

## 8. Agent Specialization e Role-Based Architecture {#agent-specialization}

### Concetti Teorici

La **specializzazione degli agenti** è un principio architetturale che assegna ruoli specifici a diversi agenti, ciascuno ottimizzato per un dominio particolare. Questo approccio migliora:

- **Efficienza**: Ogni agente è esperto nel proprio dominio
- **Manutenibilità**: Separazione chiara delle responsabilità
- **Scalabilità**: Facile aggiunta di nuove specializzazioni
- **Quality**: Risultati migliori attraverso expertise focalizzata

#### Patterns di Specializzazione

1. **Domain Specialization**: Specializzazione per settore (finance, healthcare, legal)
2. **Task Specialization**: Specializzazione per tipo di task (analysis, generation, validation)
3. **Technical Specialization**: Specializzazione per tecnologia (databases, APIs, file systems)
4. **Hybrid Specialization**: Combinazione di diversi tipi di specializzazione

---

## 9. Error Recovery e Resilience Patterns {#error-recovery}

### Concetti Teorici

I **pattern di resilienza** garantiscono che i sistemi agentici continuino a funzionare anche in presenza di errori. Strategie chiave includono:

#### Strategie di Recovery

1. **Retry with Backoff**: Tentativo ripetuto con delay crescente
2. **Circuit Breaker**: Interruzione automatica di servizi fallimentari
3. **Fallback Mechanisms**: Strategie alternative quando il path principale fallisce
4. **Graceful Degradation**: Riduzione delle funzionalità mantenendo operatività di base

#### Tipi di Errori

- **Transient Errors**: Errori temporanei (network timeout, rate limiting)
- **Persistent Errors**: Errori che richiedono intervento (API key invalida)
- **Cascading Failures**: Errori che si propagano attraverso il sistema
- **Resource Exhaustion**: Esaurimento di risorse (memoria, CPU, quota API)

---

## 10. Performance Optimization Strategies {#performance-optimization}

### Concetti Teorici

L'**ottimizzazione delle performance** nei sistemi agentici richiede approcci multi-dimensionali:

#### Dimensioni di Ottimizzazione

1. **Latency Optimization**: Riduzione del tempo di risposta
2. **Throughput Optimization**: Massimizzazione del numero di richieste gestite
3. **Resource Optimization**: Utilizzo efficiente di CPU, memoria, rete
4. **Cost Optimization**: Minimizzazione dei costi operativi (API calls, compute)

#### Tecniche di Ottimizzazione

- **Caching Intelligente**: Cache multi-livello con invalidazione automatica
- **Request Batching**: Aggregazione di richieste per ridurre overhead
- **Parallel Processing**: Esecuzione parallela di task indipendenti
- **Load Balancing**: Distribuzione del carico tra agenti multipli
- **Prompt Optimization**: Ottimizzazione dei prompt per ridurre token usage

#### Monitoring e Metriche

Metriche chiave per monitoraggio performance:

```python
class PerformanceMetrics:
    """Metriche di performance per sistemi agentici."""

    def __init__(self):
        self.latency_percentiles = {}  # P50, P95, P99
        self.throughput_rps = 0.0     # Requests per second
        self.error_rate = 0.0         # Percentuale errori
        self.resource_utilization = {}  # CPU, memoria, etc.
        self.cost_per_request = 0.0   # Costo medio per richiesta
        self.cache_hit_rate = 0.0     # Tasso di hit della cache
        self.token_usage = {          # Utilizzo token
            'input_tokens': 0,
            'output_tokens': 0,
            'total_cost': 0.0
        }
```

---

## Conclusioni e Considerazioni Avanzate

### Evoluzione dell'Agentic AI

L'Agentic AI rappresenta un cambio paradigmatico verso sistemi autonomi e intelligenti. I concetti trattati in questa guida formano le fondamenta per:

#### Tendenze Emergenti

1. **Swarm Intelligence**: Coordinazione di large-scale agent swarms
2. **Self-Improving Agents**: Agenti che migliorano autonomamente le proprie capacità
3. **Ethical AI Governance**: Framework etici integrati nell'architettura
4. **Cross-Modal Agents**: Agenti che operano su testo, immagini, audio simultaneamente

#### Sfide Future

- **Scalability**: Gestione di migliaia di agenti specializzati
- **Interoperability**: Standard per comunicazione inter-agent
- **Explainability**: Comprensione dei processi decisionali complessi
- **Security**: Protezione da attacchi adversarial e misuse

#### Best Practices Emergenti

1. **Design for Observability**: Sistemi intrinsecamente osservabili
2. **Principle of Least Privilege**: Agenti con permessi minimi necessari
3. **Continuous Learning**: Miglioramento continuo basato su feedback
4. **Human-in-the-Loop**: Integrazione dell'oversight umano nei processi critici

### Raccomandazioni per Implementation

Per implementare con successo sistemi di Agentic AI:

1. **Start Small**: Inizia con un singolo agente specializzato
2. **Measure Everything**: Implementa monitoring completo fin dall'inizio
3. **Design for Failure**: Assumi che i componenti falliranno
4. **Iterate Rapidly**: Cicli di feedback rapidi per miglioramento continuo
5. **Think Security**: Considera implicazioni di sicurezza in ogni design decision

L'Agentic AI non è solo una tecnologia, ma un nuovo paradigma di computing che richiede ripensamento di architetture, processi e governance. La padronanza di questi concetti avanzati ti posiziona all'avanguardia di questa rivoluzione tecnologica.
