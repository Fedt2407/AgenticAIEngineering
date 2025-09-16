# Guida Completa ai Guardrails nell'Agentic AI

## Indice

1. [Introduzione Teorica](#introduzione-teorica)
2. [Tipi di Guardrails](#tipi-di-guardrails)
3. [Implementazione Pratica](#implementazione-pratica)
4. [Esempi di Codice Dettagliati](#esempi-di-codice-dettagliati)
5. [Best Practices](#best-practices)
6. [Monitoraggio e Debugging](#monitoraggio-e-debugging)

## Introduzione Teorica

I **guardrails** nell'Agentic AI rappresentano un sistema di controlli e vincoli progettati per garantire che gli agenti AI operino in modo sicuro, etico e conforme alle aspettative. Sono essenzialmente delle "barriere di sicurezza" che impediscono agli agenti di eseguire azioni indesiderate o potenzialmente dannose.

### Perché sono Fondamentali?

1. **Sicurezza**: Prevengono azioni pericolose o distruttive
2. **Conformità**: Assicurano il rispetto di regolamenti e politiche
3. **Affidabilità**: Mantengono il comportamento dell'agente entro parametri prevedibili
4. **Trust**: Aumentano la fiducia degli utenti nel sistema
5. **Controllo**: Permettono un controllo granulare sul comportamento dell'agente

### Principi Fondamentali

- **Fail-Safe**: In caso di dubbio, l'agente deve fallire in modo sicuro
- **Trasparenza**: Le decisioni dei guardrails devono essere tracciabili
- **Configurabilità**: I guardrails devono essere adattabili a diversi contesti
- **Performance**: Non devono compromettere significativamente le prestazioni

## Tipi di Guardrails

### 1. Input Validation Guardrails

Controllano e validano gli input prima che raggiungano l'agente.

### 2. Output Filtering Guardrails

Filtrano e modificano gli output dell'agente prima che vengano restituiti.

### 3. Behavioral Guardrails

Monitorano il comportamento dell'agente durante l'esecuzione.

### 4. Resource Guardrails

Limitano l'uso delle risorse (tempo, memoria, API calls). Evitano uso eccessivo delle risorse.

### 5. Contextual Guardrails

Applicano regole basate sul contesto specifico della conversazione.
Mantengon il contesto della conversazione allineato al tema che si sta trattando ed evitano allucinazioni dell'LLM.

### 6. Ethical Guardrails

Assicurano che l'agente rispetti principi etici e morali.

## Implementazione Pratica

L'implementazione dei guardrails può avvenire a diversi livelli:

1. **Pre-processing**: Validazione e sanitizzazione degli input prima dell'elaborazione. Include controlli sulla lunghezza, formato, contenuto inappropriato e potenziali rischi di sicurezza.

2. **Durante l'esecuzione**: Sistema di monitoraggio che verifica costantemente il comportamento dell'agente, controllando l'uso delle risorse, il tempo di esecuzione, e assicurando che le azioni rimangano entro i limiti prestabiliti.

3. **Post-processing**: Analisi approfondita dell'output generato, verificando la qualità, la coerenza, la sicurezza e la conformità alle policy prima di restituirlo all'utente finale.

4. **Meta-level**: Sistema sofisticato di controllo che supervisiona e coordina tutti gli altri guardrails, adattando dinamicamente le regole in base al contesto e all'esperienza accumulata. Include anche meccanismi di auto-diagnostica e auto-correzione.

## Esempi di Codice Dettagliati

### Esempio 1: Sistema Base di Guardrails con Input/Output Validation

```python
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

# Configurazione del logging per tracciare le attivazioni dei guardrails
# Utilizziamo logging invece di Trace perché:
# 1. Logging è una libreria standard di Python, più leggera e adatta per il monitoraggio base
# 2. Trace è più adatto per il profiling e debugging dettagliato del codice
# 3. In questo caso vogliamo solo registrare le attivazioni dei guardrails, non analizzare
#    l'esecuzione del codice riga per riga
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardrailSeverity(Enum):
    """
    Enumeration per definire i livelli di severità dei guardrails
    """
    INFO = "info"           # Informativo, non blocca l'esecuzione
    WARNING = "warning"     # Avviso, logga ma continua
    ERROR = "error"         # Errore, blocca l'esecuzione
    CRITICAL = "critical"   # Critico, blocca e notifica amministratori

@dataclass
class GuardrailResult:
    """
    Classe per rappresentare il risultato di un controllo guardrail
    """
    passed: bool                                # Se il controllo è passato
    rule_name: str                              # Nome della regola applicata
    severity: GuardrailSeverity                 # Livello di severità preso dalle enumerazioni della classe precedentemente definita
    message: str                                # Messaggio descrittivo
    modified_content: Optional[str] = None      # Contenuto modificato (se applicabile)
    metadata: Dict[str, Any] = None             # Metadati aggiuntivi

# Classe base astratta che definisce l'interfaccia e la logica comune per tutti i guardrail.
# Ogni guardrail specifico dovrà estendere questa classe implementando la propria logica di validazione.
class BaseGuardrail:
    """
    Classe base astratta che definisce l'interfaccia standard per i guardrail.

    Fornisce:
    - Inizializzazione con nome e livello di severità
    - Conteggio e timestamp delle attivazioni
    - Logging automatico delle attivazioni
    - Metodo check() astratto da implementare nelle sottoclassi

    Attributes:
        name (str): Nome identificativo del guardrail
        severity (GuardrailSeverity): Livello di severità delle violazioni
        activation_count (int): Numero di volte che il guardrail è stato attivato
        last_activation (datetime): Timestamp dell'ultima attivazione
    """
    def __init__(self, name: str, severity: GuardrailSeverity = GuardrailSeverity.ERROR):
        self.name = name
        self.severity = severity
        self.activation_count = 0  # Contatore delle attivazioni
        self.last_activation = None

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Metodo astratto da implementare in ogni guardrail specifico
        """
        raise NotImplementedError("Ogni guardrail deve implementare il metodo check")

    def _log_activation(self, result: GuardrailResult):
        """
        Metodo privato per loggare l'attivazione del guardrail
        """
        self.activation_count += 1
        self.last_activation = datetime.now()

        log_level = {
            GuardrailSeverity.INFO: logging.INFO,
            GuardrailSeverity.WARNING: logging.WARNING,
            GuardrailSeverity.ERROR: logging.ERROR,
            GuardrailSeverity.CRITICAL: logging.CRITICAL
        }[result.severity]

        logger.log(log_level, f"Guardrail '{self.name}' attivato: {result.message}")

class ProfanityGuardrail(BaseGuardrail):
    """
    Guardrail per filtrare contenuti con linguaggio inappropriato
    """
    def __init__(self, severity: GuardrailSeverity = GuardrailSeverity.WARNING):
        super().__init__("ProfanityFilter", severity)
        # Lista di parole inappropriate (esempio semplificato)
        self.blocked_words = [
            "maledetto", "dannato", "cazzo", "merda",
            "bastardo", "stronzo", "idiota", "cretino"
        ]
        # Pattern per rilevare tentativi di evasion (es. c@zzo)
        self.evasion_patterns = [
            r'[c|C][@4]zz[o0]',  # Rileva c@zzo, c4zzo, ecc.
            r'[m|M][e3]rd[@4]',  # Rileva m3rd@, merd4, ecc.
        ]

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla se il contenuto contiene linguaggio inappropriato
        """
        content_lower = content.lower()
        violations = []

        # Controllo parole dirette
        for word in self.blocked_words:
            if word in content_lower:
                violations.append(f"Parola inappropriata trovata: {word}")

        # Controllo pattern di evasion
        for pattern in self.evasion_patterns:
            # re è il modulo di Python per le espressioni regolari (Regular Expressions)
            # re.search cerca una corrispondenza del pattern ovunque nella stringa content
            # re.IGNORECASE rende la ricerca case-insensitive (non distingue maiuscole/minuscole)
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Pattern di evasion rilevato: {pattern}")

        if violations:
            # Se ci sono violazioni, creiamo un contenuto censurato
            modified_content = content
            for word in self.blocked_words:
                # Sostituiamo ogni lettera della parola inappropriata con *
                modified_content = re.sub(
                    re.escape(word),
                    '*' * len(word),
                    modified_content,
                    flags=re.IGNORECASE
                )

            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Linguaggio inappropriato rilevato: {', '.join(violations)}",
                modified_content=modified_content,
                metadata={"violations": violations, "original_length": len(content)}
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message="Nessun linguaggio inappropriato rilevato"
            )

        self._log_activation(result)
        return result

class PIIGuardrail(BaseGuardrail):
    """
    Guardrail per rilevare e proteggere informazioni personali identificabili (PII)
    """
    def __init__(self, severity: GuardrailSeverity = GuardrailSeverity.ERROR):
        super().__init__("PIIProtection", severity)

        # Pattern regex per rilevare diversi tipi di PII
        self.pii_patterns = {
            'codice_fiscale': r'[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'telefono': r'(\+39)?[\s-]?([0-9]{2,4})[\s-]?([0-9]{3,4})[\s-]?([0-9]{3,4})',
            'carta_credito': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'iban': r'IT\d{2}[A-Z]\d{22}',
        }

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Rileva presenza di informazioni personali nel contenuto
        """
        detected_pii = {}
        modified_content = content

        # Scansione per ogni tipo di PII
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                detected_pii[pii_type] = matches
                # Censura le informazioni trovate
                modified_content = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', modified_content)

        if detected_pii:
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Informazioni personali rilevate: {list(detected_pii.keys())}",
                modified_content=modified_content,
                metadata={
                    "detected_pii_types": list(detected_pii.keys()),
                    "total_matches": sum(len(matches) for matches in detected_pii.values())
                }
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message="Nessuna informazione personale rilevata"
            )

        self._log_activation(result)
        return result

class ContentLengthGuardrail(BaseGuardrail):
    """
    Guardrail per controllare la lunghezza del contenuto
    """
    def __init__(self, max_length: int = 1000, min_length: int = 1, severity: GuardrailSeverity = GuardrailSeverity.WARNING):
        # Chiama il costruttore della classe base BaseGuardrail passando il nome "ContentLength"
        # e il livello di severità per inizializzare gli attributi base del guardrail
        # In pratica qualifica i due parametri (name e severity) revisti dalla classe base
        super().__init__("ContentLength", severity)
        # Aggiunge i nuovi parametri previsti per questa classe specifica
        self.max_length = max_length
        self.min_length = min_length

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla che la lunghezza del contenuto sia nei limiti accettabili
        """
        content_length = len(content)

        if content_length > self.max_length:
            # Tronca il contenuto se troppo lungo
            modified_content = content[:self.max_length] + "... [TRONCATO]"
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Contenuto troppo lungo: {content_length} caratteri (max: {self.max_length})",
                modified_content=modified_content,
                metadata={"original_length": content_length, "truncated": True}
            )
        elif content_length < self.min_length:
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Contenuto troppo corto: {content_length} caratteri (min: {self.min_length})",
                metadata={"original_length": content_length}
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message=f"Lunghezza contenuto accettabile: {content_length} caratteri",
                metadata={"content_length": content_length}
            )

        self._log_activation(result)
        return result

class GuardrailEngine:
    """
    Motore principale per gestire e eseguire tutti i guardrails.

    Questa classe fornisce un sistema centralizzato per la gestione e l'esecuzione di guardrails
    sia per gli input che per gli output. I guardrails sono meccanismi di validazione e controllo
    che possono essere configurati per verificare e potenzialmente modificare i contenuti.

    Caratteristiche principali:
    - Gestione separata di guardrails per input e output
    - Logging automatico delle esecuzioni
    - Possibilità di modificare i contenuti durante la validazione
    - Sistema di severità per gestire diversi livelli di violazioni
    - Raccolta di statistiche sull'utilizzo dei guardrails

    Attributes:
        input_guardrails (List[BaseGuardrail]): Lista dei guardrails per la validazione degli input
        output_guardrails (List[BaseGuardrail]): Lista dei guardrails per la validazione degli output
        execution_log (List[Dict[str, Any]]): Storico delle esecuzioni dei guardrails
    """
    def __init__(self):
        self.input_guardrails: List[BaseGuardrail] = []   # Guardrails per input (Lista)
        self.output_guardrails: List[BaseGuardrail] = []  # Guardrails per output (Lista)
        self.execution_log: List[Dict[str, Any]] = []     # Log delle esecuzioni (Lista di dizionari)

    def add_input_guardrail(self, guardrail: BaseGuardrail):
        """
        Aggiunge un guardrail per la validazione degli input
        """
        self.input_guardrails.append(guardrail)
        logger.info(f"Aggiunto input guardrail: {guardrail.name}")

    def add_output_guardrail(self, guardrail: BaseGuardrail):
        """
        Aggiunge un guardrail per la validazione degli output
        """
        self.output_guardrails.append(guardrail)
        logger.info(f"Aggiunto output guardrail: {guardrail.name}")

    def validate_input(self, content: str, context: Dict[str, Any] = None) -> Tuple[bool, str, List[GuardrailResult]]:
        """
        Esegue tutti i guardrails di input sul contenuto fornito

        Returns:
            Tuple[bool, str, List[GuardrailResult]]:
            - bool: se la validazione è passata
            - str: contenuto (possibilmente modificato)
            - List[GuardrailResult]: risultati di tutti i guardrails
        """
        results = []
        modified_content = content
        overall_passed = True

        # Log dell'inizio della validazione input
        logger.info(f"Inizio validazione input: {len(self.input_guardrails)} guardrails da eseguire")

        # Esecuzione di ogni guardrail di input
        for guardrail in self.input_guardrails:
            result = guardrail.check(modified_content, context)
            results.append(result)

            # Se il guardrail ha modificato il contenuto, usiamo quello modificato
            if result.modified_content is not None:
                modified_content = result.modified_content

            # Se un guardrail critico o di errore fallisce, blocchiamo tutto
            if not result.passed and result.severity in [GuardrailSeverity.ERROR, GuardrailSeverity.CRITICAL]:
                overall_passed = False
                logger.error(f"Guardrail {guardrail.name} ha bloccato l'input")

        # Registrazione nel log delle esecuzioni
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "input_validation",
            "passed": overall_passed,
            "guardrails_count": len(self.input_guardrails),
            "failed_guardrails": [r.rule_name for r in results if not r.passed],
            "content_modified": modified_content != content
        })

        return overall_passed, modified_content, results

    def validate_output(self, content: str, context: Dict[str, Any] = None) -> Tuple[bool, str, List[GuardrailResult]]:
        """
        Esegue tutti i guardrails di output sul contenuto fornito
        """
        results = []
        modified_content = content
        overall_passed = True

        logger.info(f"Inizio validazione output: {len(self.output_guardrails)} guardrails da eseguire")

        for guardrail in self.output_guardrails:
            result = guardrail.check(modified_content, context)
            results.append(result)

            if result.modified_content is not None:
                modified_content = result.modified_content

            if not result.passed and result.severity in [GuardrailSeverity.ERROR, GuardrailSeverity.CRITICAL]:
                overall_passed = False
                logger.error(f"Guardrail {guardrail.name} ha bloccato l'output")

        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "output_validation",
            "passed": overall_passed,
            "guardrails_count": len(self.output_guardrails),
            "failed_guardrails": [r.rule_name for r in results if not r.passed],
            "content_modified": modified_content != content
        })

        return overall_passed, modified_content, results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Restituisce statistiche sull'uso dei guardrails
        """
        all_guardrails = self.input_guardrails + self.output_guardrails

        stats = {
            "total_guardrails": len(all_guardrails),
            "input_guardrails": len(self.input_guardrails),
            "output_guardrails": len(self.output_guardrails),
            "total_executions": len(self.execution_log),
            "guardrail_activations": {
                guardrail.name: {
                    "activation_count": guardrail.activation_count,
                    # isoformat() converte un oggetto datetime in una stringa ISO 8601 (es: "2024-01-24T10:30:15.123456")
                    "last_activation": guardrail.last_activation.isoformat() if guardrail.last_activation else None
                }
                for guardrail in all_guardrails
            }
        }

        return stats

# Esempio di utilizzo del sistema
def esempio_utilizzo_guardrails():
    """
    Funzione di esempio che mostra come utilizzare il sistema di guardrails
    """
    print("=== ESEMPIO UTILIZZO SISTEMA GUARDRAILS ===\n")

    # Creazione del motore dei guardrails
    engine = GuardrailEngine()

    # Aggiunta dei guardrails di input
    engine.add_input_guardrail(PIIGuardrail(GuardrailSeverity.ERROR))
    engine.add_input_guardrail(ContentLengthGuardrail(max_length=200, severity=GuardrailSeverity.WARNING))

    # Aggiunta dei guardrails di output
    engine.add_output_guardrail(ProfanityGuardrail(GuardrailSeverity.WARNING))

    # Test con diversi tipi di input
    test_inputs = [
        "Ciao, il mio codice fiscale è RSSMRA80A01H501Z",
        "Questo è un messaggio molto molto molto lungo che supera il limite di caratteri impostato nel guardrail per testare il troncamento automatico del contenuto quando è troppo lungo",
        "Questo è un messaggio pulito senza problemi",
        "Maledetto computer non funziona!"
    ]

    # enumerate() crea un oggetto enumeratore che associa un contatore (i) ad ogni elemento dell'iterabile (test_inputs)
    # il parametro 1 indica il valore iniziale del contatore (di default partirebbe da 0)
    # Esempio: se test_inputs = ['a', 'b', 'c'] allora enumerate(test_inputs, 1) produce:
    # 1, 'a'
    # 2, 'b'
    # 3, 'c'
    # NOTA: senza specificare 1 come secondo parametro dopo test_inputs, il contatore partirebbe da zero producendo:
    # 0, 'a'
    # 1, 'b'
    # 2, 'c'
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n--- TEST {i} ---")
        print(f"Input originale: {test_input}")

        # Validazione input ("engine" è l'istanza della classe "GuradrailEngine")
        input_passed, modified_input, input_results = engine.validate_input(test_input) # attribuisce alle 3 variabili gli output del metodo validate_input della classe engine (istanza della classe GuardrailEngine)
        print(f"Input validato: {input_passed}")
        if modified_input != test_input:
            print(f"Input modificato: {modified_input}")

        # Se l'input passa la validazione, simula una risposta e valida l'output
        if input_passed:
            simulated_response = f"Ho ricevuto il tuo messaggio: {modified_input}. Che cazzo di risposta vuoi?"

            output_passed, modified_output, output_results = engine.validate_output(simulated_response)
            print(f"Output validato: {output_passed}")
            if modified_output != simulated_response:
                print(f"Output modificato: {modified_output}")

        print("-" * 50) # crea una linea di trattini per separare i contenuti stampati a terminale

    # Stampa delle statistiche finali
    print("\n=== STATISTICHE FINALI ===")
    stats = engine.get_statistics()
    print(json.dumps(stats, indent=2, default=str))

# Esecuzione dell'esempio se il file viene eseguito direttamente
if __name__ == "__main__":
    esempio_utilizzo_guardrails()
```

### Esempio 2: Guardrails Avanzati con Context Awareness

```python
from typing import Set, Dict, List, Any, Optional
from datetime import datetime, timedelta
# hashlib fornisce funzioni di hashing crittografico come MD5, SHA1, SHA256 ecc.
import hashlib

class ContextAwareGuardrail(BaseGuardrail):
    """
    Guardrail avanzato che considera il contesto della conversazione
    """
    def __init__(self, name: str, severity: GuardrailSeverity = GuardrailSeverity.WARNING):
        super().__init__(name, severity)
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {}
        self.session_data: Dict[str, Any] = {}

    def update_context(self, user_message: str, agent_response: str, user_id: str, session_id: str, metadata: Dict[str, Any] = None):
        """
        Aggiorna il contesto della conversazione per future validazioni
        """
        context_entry = {
            "timestamp": datetime.now(),
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }

        # Mantiene solo gli ultimi 50 messaggi per performance
        self.conversation_history.append(context_entry)
        if len(self.conversation_history) > 50:
            self.conversation_history.pop(0) # rimuove il 51-esimo contenuto più vecchio

class RepetitionGuardrail(ContextAwareGuardrail):
    """
    Guardrail che rileva e previene risposte ripetitive
    """
    def __init__(self, max_similarity: float = 0.8, lookback_messages: int = 5):
        super().__init__("RepetitionPrevention", GuardrailSeverity.WARNING) # Attribuisce i valori ai parametri name e severity della classe base
        self.max_similarity = max_similarity  # Soglia di similarità (0-1)
        self.lookback_messages = lookback_messages  # Quanti messaggi precedenti controllare

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcola la similarità tra due testi usando un metodo semplice
        In produzione si potrebbero usare algoritmi più sofisticati come cosine similarity
        """
        # Normalizza i testi
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Calcola la Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if len(union) == 0:
            return 0.0

        return len(intersection) / len(union)

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla se il contenuto è troppo simile a risposte precedenti
        """
        if not self.conversation_history:
            return GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message="Nessuna conversazione precedente per il confronto"
            )

        # Prende gli ultimi N messaggi dell'agente
        recent_responses = [
            entry["agent_response"]
            for entry in self.conversation_history[-self.lookback_messages:] # prende unicamente gli ultimi messaggi sui quali fare il controllo
            if entry["agent_response"]
        ]

        max_similarity_found = 0.0
        similar_response = None

        # Controlla la similarità con ogni risposta precedente
        for previous_response in recent_responses:
            similarity = self.calculate_similarity(content, previous_response)
            if similarity > max_similarity_found:
                max_similarity_found = similarity
                similar_response = previous_response

        if max_similarity_found > self.max_similarity:
            # Genera una risposta modificata aggiungendo variazione
            modified_content = f"Come ho già menzionato, {content.lower()}" # Se la similarità supera la soglia viene richimato il messaggio precedente similare

            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Risposta troppo ripetitiva (similarità: {max_similarity_found:.2f})",
                modified_content=modified_content,
                metadata={
                    "similarity_score": max_similarity_found,
                    "threshold": self.max_similarity,
                    "similar_response_preview": similar_response[:100] + "..." if similar_response else None
                }
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message=f"Contenuto sufficientemente unico (max similarità: {max_similarity_found:.2f})"
            )

        self._log_activation(result)
        return result

class RateLimitingGuardrail(ContextAwareGuardrail):
    """
    Guardrail che implementa rate limiting per prevenire abusi
    """
    def __init__(self, max_requests_per_minute: int = 10, max_requests_per_hour: int = 100):
        super().__init__("RateLimiting", GuardrailSeverity.ERROR)
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
        self.request_timestamps: List[datetime] = []

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla se l'utente ha superato i limiti di rate
        """
        now = datetime.now()

        # Rimuove le richieste più vecchie di un'ora
        self.request_timestamps = [
            timestamp for timestamp in self.request_timestamps
            if now - timestamp < timedelta(hours=1)
        ]

        # Conta le richieste nell'ultimo minuto
        recent_requests = [
            timestamp for timestamp in self.request_timestamps
            if now - timestamp < timedelta(minutes=1)
        ]

        # Registra questa richiesta
        self.request_timestamps.append(now)

        # Controlla i limiti
        if len(recent_requests) > self.max_requests_per_minute:
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Rate limit superato: {len(recent_requests)} richieste nell'ultimo minuto (max: {self.max_requests_per_minute})",
                metadata={
                    "requests_last_minute": len(recent_requests),
                    "requests_last_hour": len(self.request_timestamps),
                    "limit_minute": self.max_requests_per_minute,
                    "limit_hour": self.max_requests_per_hour
                }
            )
        elif len(self.request_timestamps) > self.max_requests_per_hour:
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Rate limit superato: {len(self.request_timestamps)} richieste nell'ultima ora (max: {self.max_requests_per_hour})",
                metadata={
                    "requests_last_minute": len(recent_requests),
                    "requests_last_hour": len(self.request_timestamps),
                    "limit_minute": self.max_requests_per_minute,
                    "limit_hour": self.max_requests_per_hour
                }
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message=f"Rate limit OK: {len(recent_requests)}/min, {len(self.request_timestamps)}/hour"
            )

        self._log_activation(result)
        return result

class TopicDriftGuardrail(ContextAwareGuardrail):
    """
    Guardrail che monitora la deriva del topic nella conversazione
    """
    def __init__(self, allowed_topics: Set[str], max_drift_score: float = 0.7):
        super().__init__("TopicDrift", GuardrailSeverity.WARNING)
        self.allowed_topics = allowed_topics
        self.max_drift_score = max_drift_score

        # Keywords associati a ogni topic (semplificato)
        self.topic_keywords = {
            "tecnologia": ["computer", "software", "programmazione", "AI", "algoritmo", "codice"],
            "salute": ["medicina", "dottore", "ospedale", "malattia", "cura", "terapia"],
            "finanza": ["denaro", "investimento", "banca", "prestito", "budget", "economia"],
            "viaggi": ["vacanza", "hotel", "volo", "destinazione", "turismo", "viaggio"]
        }

    def calculate_topic_score(self, content: str, topic: str) -> float:
        """
        Calcola quanto il contenuto è relativo a un determinato topic
        """
        if topic not in self.topic_keywords:
            return 0.0

        content_words = set(content.lower().split())
        topic_words = set(self.topic_keywords[topic])

        # Conta le parole in comune
        common_words = content_words.intersection(topic_words)

        if len(content_words) == 0:
            return 0.0

        # Score basato sulla proporzione di parole topic-relevant
        return len(common_words) / len(content_words)

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla se il contenuto deriva troppo dai topic consentiti
        """
        # Calcola il punteggio per ogni topic consentito
        topic_scores = {}
        max_score = 0.0
        best_topic = None

        for topic in self.allowed_topics:
            score = self.calculate_topic_score(content, topic)
            topic_scores[topic] = score

            if score > max_score:
                max_score = score
                best_topic = topic

        # Se il punteggio massimo è sotto la soglia, c'è deriva del topic
        if max_score < self.max_drift_score:
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Topic drift rilevato. Miglior match: {best_topic} (score: {max_score:.2f})",
                modified_content=f"Mi scuso, ma preferirei restare sui topic di {', '.join(self.allowed_topics)}. {content}",
                metadata={
                    "topic_scores": topic_scores,
                    "max_score": max_score,
                    "threshold": self.max_drift_score,
                    "best_topic": best_topic
                }
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message=f"Topic appropriato: {best_topic} (score: {max_score:.2f})",
                metadata={"topic_scores": topic_scores, "best_topic": best_topic}
            )

        self._log_activation(result)
        return result

# Esempio di Sistema Avanzato con Context Awareness
def esempio_guardrails_avanzati():
    """
    Esempio che mostra l'uso di guardrails context-aware per la validazione avanzata di input e output.
    Implementa controlli per:
    - Ripetizioni nel contenuto
    - Rate limiting delle richieste
    - Deriva dei topic rispetto a quelli consentiti
    """
    print("=== ESEMPIO GUARDRAILS AVANZATI ===\n")

    # Configurazione del sistema avanzato -> Inzializza la classe principale
    engine = GuardrailEngine()

    # Aggiunta guardrails context-aware -> Inizializza le rispettive classi specifiche per i controlli richiesti
    repetition_guard = RepetitionGuardrail(max_similarity=0.7, lookback_messages=3)
    rate_limit_guard = RateLimitingGuardrail(max_requests_per_minute=5, max_requests_per_hour=20)
    topic_guard = TopicDriftGuardrail(
        allowed_topics={"tecnologia", "programmazione", "AI"},
        max_drift_score=0.3
    )

    # Applica i metodi per controllare input e output alle instanze di classe appena definite
    engine.add_output_guardrail(repetition_guard)
    engine.add_input_guardrail(rate_limit_guard)
    engine.add_output_guardrail(topic_guard)

    # Simulazione di una conversazione con context
    conversation_pairs = [
        ("Come funziona l'AI?", "L'intelligenza artificiale funziona attraverso algoritmi complessi che processano dati."),
        ("Spiegami ancora l'AI", "L'intelligenza artificiale funziona attraverso algoritmi complessi che analizzano informazioni."),  # Ripetitiva
        ("Cosa pensi del calcio?", "Il calcio è uno sport interessante con molte strategie tattiche."),  # Topic drift
        ("Come programmare in Python?", "Python è un linguaggio di programmazione versatile e facile da imparare."),
        ("Ancora Python per favore", "Python offre sintassi chiara e molte librerie per sviluppatori."),
    ]

    user_id = "user_123"
    session_id = "session_456"

    for i, (user_msg, agent_response) in enumerate(conversation_pairs, 1):
        print(f"\n--- CONVERSAZIONE {i} ---")
        print(f"Utente: {user_msg}")

        # Validazione input (rate limiting) -> associa alle 3 variabili quanto ritornato dal metodo validate_input
        input_passed, modified_input, input_results = engine.validate_input(
            user_msg,
            context={"user_id": user_id, "session_id": session_id}
        )

        if not input_passed:
            print("❌ Input bloccato dai guardrails")
            for result in input_results:
                if not result.passed:
                    print(f"  - {result.message}")
            continue

        # Validazione output (ripetizione e topic drift) -> associa alle 3 variabili quanto ritornato dal metodo validate_output
        output_passed, modified_output, output_results = engine.validate_output(
            agent_response,
            context={"user_id": user_id, "session_id": session_id}
        )

        if output_passed:
            print(f"Agente: {agent_response}")
        else:
            print(f"Agente (modificato): {modified_output}")
            for result in output_results:
                if not result.passed:
                    print(f"  ⚠️ {result.message}")

        # Aggiorna il contesto per i guardrails context-aware
        repetition_guard.update_context(user_msg, modified_output or agent_response, user_id, session_id)
        topic_guard.update_context(user_msg, modified_output or agent_response, user_id, session_id)

        print("-" * 60)

    # Statistiche finali
    print("\n=== STATISTICHE AVANZATE ===")
    stats = engine.get_statistics()

    # Aggiunge statistiche specifiche per guardrails context-aware
    stats["context_aware_stats"] = {
        "repetition_guard": {
            "conversation_history_length": len(repetition_guard.conversation_history),
            "max_similarity_threshold": repetition_guard.max_similarity
        },
        "rate_limit_guard": {
            "total_requests_tracked": len(rate_limit_guard.request_timestamps),
            "limits": {
                "per_minute": rate_limit_guard.max_requests_per_minute,
                "per_hour": rate_limit_guard.max_requests_per_hour
            }
        },
        "topic_guard": {
            "allowed_topics": list(topic_guard.allowed_topics),
            "drift_threshold": topic_guard.max_drift_score
        }
    }

    print(json.dumps(stats, indent=2, default=str))

if __name__ == "__main__":
    esempio_guardrails_avanzati()
```

### Esempio 3: Guardrails per API e Risorse Esterne

```python
import time
import requests
from typing import Dict, Any, Optional, List
# unittest.mock fornisce classi per simulare oggetti e comportamenti durante i test
# Mock è una classe che crea oggetti fittizi che possono imitare qualsiasi altro oggetto
from unittest.mock import Mock
import json

class APICallGuardrail(BaseGuardrail):
    """
    Guardrail per controllare e limitare le chiamate API esterne
    """
    def __init__(self, allowed_domains: Set[str], max_calls_per_minute: int = 10, timeout_seconds: int = 5, severity: GuardrailSeverity = GuardrailSeverity.ERROR):
        super().__init__("APICallControl", severity)
        self.allowed_domains = allowed_domains
        self.max_calls_per_minute = max_calls_per_minute
        self.timeout_seconds = timeout_seconds
        self.call_history: List[Dict[str, Any]] = []

    def is_domain_allowed(self, url: str) -> bool:
        """
        Verifica se il dominio dell'URL è nella lista dei domini permessi
        """
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            # Rimuove 'www.' se presente
            if domain.startswith('www.'):
                domain = domain[4:]

            return domain in self.allowed_domains
        except Exception:
            return False

    def check_rate_limit(self) -> bool:
        """
        Controlla se siamo sotto il limite di rate per le chiamate API
        """
        now = time.time()
        # Filtra le chiamate dell'ultimo minuto
        recent_calls = [
            call for call in self.call_history
            if now - call['timestamp'] < 60  # 60 secondi
        ]

        return len(recent_calls) < self.max_calls_per_minute

    def validate_api_call(self, url: str, method: str = 'GET', headers: Dict[str, str] = None) -> GuardrailResult:
        """
        Valida una chiamata API prima che venga eseguita
        Utilizza i metodi definiti poco sopra per effettuare i controlli
        """
        # Controllo 1: Dominio permesso
        if not self.is_domain_allowed(url):
            return GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Dominio non autorizzato: {url}",
                metadata={"url": url, "allowed_domains": list(self.allowed_domains)}
            )

        # Controllo 2: Rate limiting
        if not self.check_rate_limit():
            return GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message="Rate limit superato per chiamate API",
                metadata={
                    "calls_last_minute": len([
                        c for c in self.call_history
                        if time.time() - c['timestamp'] < 60
                    ]),
                    "max_calls_per_minute": self.max_calls_per_minute
                }
            )

        # Controllo 3: Headers pericolosi
        dangerous_headers = ['authorization', 'x-api-key', 'cookie']
        if headers:
            for header_name in headers.keys():
                if header_name.lower() in dangerous_headers:
                    return GuardrailResult(
                        passed=False,
                        rule_name=self.name,
                        severity=GuardrailSeverity.WARNING,
                        message=f"Header potenzialmente pericoloso: {header_name}",
                        metadata={"dangerous_header": header_name}
                    )

        # Se tutti i controlli passano, registra la chiamata
        self.call_history.append({
            "timestamp": time.time(),
            "url": url,
            "method": method,
            "headers_count": len(headers) if headers else 0
        })

        return GuardrailResult(
            passed=True,
            rule_name=self.name,
            severity=GuardrailSeverity.INFO,
            message="Chiamata API autorizzata",
            metadata={"url": url, "method": method}
        )

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Implementazione del metodo check base (per compatibilità)
        """
        # Cerca pattern di URL nel contenuto
        import re  # libreria per il pattern matching e le espressioni regolari (re sta per "regular expressions")
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls_found = re.findall(url_pattern, content)

        if urls_found:
            # Valida ogni URL trovato
            for url in urls_found:
                result = self.validate_api_call(url)
                if not result.passed:
                    self._log_activation(result)
                    return result

        # Se nessun URL problematico è trovato
        result = GuardrailResult(
            passed=True,
            rule_name=self.name,
            severity=GuardrailSeverity.INFO,
            message="Nessuna chiamata API problematica rilevata"
        )
        self._log_activation(result)
        return result

class ResourceUsageGuardrail(BaseGuardrail):
    """
    Guardrail per monitorare l'uso delle risorse di sistema
    """
    def __init__(self, max_memory_mb: int = 100, max_execution_time_seconds: int = 30):
        super().__init__("ResourceUsage", GuardrailSeverity.ERROR)
        self.max_memory_mb = max_memory_mb
        self.max_execution_time_seconds = max_execution_time_seconds
        self.start_time = None

    def start_monitoring(self):
        """
        Inizia il monitoraggio delle risorse
        """
        self.start_time = time.time()

    def check_memory_usage(self) -> Optional[float]:
        """
        Controlla l'uso della memoria (semplificato - in produzione usare psutil)
        """
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return memory_mb
        except ImportError:
            # Mock per l'esempio se psutil non è disponibile
            import random
            return random.uniform(50, 150)  # Simula uso memoria casuale

    def check_execution_time(self) -> Optional[float]:
        """
        Controlla il tempo di esecuzione
        """
        if self.start_time is None:
            return None
        return time.time() - self.start_time

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla l'uso delle risorse di sistema
        """
        violations = []
        metadata = {}

        # Controllo memoria
        memory_usage = self.check_memory_usage()
        if memory_usage is not None:
            metadata['memory_usage_mb'] = memory_usage
            if memory_usage > self.max_memory_mb:
                violations.append(f"Uso memoria eccessivo: {memory_usage:.1f}MB (max: {self.max_memory_mb}MB)")

        # Controllo tempo di esecuzione
        execution_time = self.check_execution_time()
        if execution_time is not None:
            metadata['execution_time_seconds'] = execution_time
            if execution_time > self.max_execution_time_seconds:
                violations.append(f"Tempo di esecuzione eccessivo: {execution_time:.1f}s (max: {self.max_execution_time_seconds}s)")

        if violations:
            result = GuardrailResult(
                passed=False,
                rule_name=self.name,
                severity=self.severity,
                message=f"Violazioni risorse: {'; '.join(violations)}",
                metadata=metadata
            )
        else:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message="Uso risorse entro i limiti",
                metadata=metadata
            )

        self._log_activation(result)
        return result

class DataValidationGuardrail(BaseGuardrail):
    """
    Guardrail per validare dati strutturati (JSON, XML, etc.)
    """
    def __init__(self, required_fields: List[str], field_types: Dict[str, type], max_nesting_level: int = 5):
        super().__init__("DataValidation", GuardrailSeverity.ERROR)
        self.required_fields = required_fields
        self.field_types = field_types
        self.max_nesting_level = max_nesting_level

    def validate_json_structure(self, json_str: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Valida la struttura di un JSON
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, f"JSON malformato: {str(e)}", {}

        violations = []
        metadata = {"parsed_data_keys": list(data.keys()) if isinstance(data, dict) else []}

        # Verifica che data sia un dizionario usando isinstance() che controlla il tipo dell'oggetto
        if not isinstance(data, dict):
            return False, "Il JSON deve essere un oggetto", metadata

        # Controllo campi richiesti
        for field in self.required_fields:
            if field not in data:
                violations.append(f"Campo richiesto mancante: {field}")

        # Controllo tipi dei campi
        for field, expected_type in self.field_types.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    violations.append(f"Tipo errato per campo {field}: atteso {expected_type.__name__}, trovato {type(data[field]).__name__}")

        # Controllo profondità di nesting
        def check_nesting_depth(obj, current_depth=0):
            if current_depth > self.max_nesting_level:
                return False

            if isinstance(obj, dict):
                for value in obj.values():
                    if not check_nesting_depth(value, current_depth + 1):
                        return False
            elif isinstance(obj, list):
                for item in obj:
                    if not check_nesting_depth(item, current_depth + 1):
                        return False

            return True

        if not check_nesting_depth(data):
            violations.append(f"Livello di nesting troppo profondo (max: {self.max_nesting_level})")

        success = len(violations) == 0
        message = "Struttura JSON valida" if success else f"Errori di validazione: {'; '.join(violations)}"

        return success, message, metadata

    def check(self, content: str, context: Dict[str, Any] = None) -> GuardrailResult:
        """
        Controlla se il contenuto contiene dati strutturati validi
        """
        # Cerca pattern JSON nel contenuto
        import re
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, content)

        if not json_matches:
            result = GuardrailResult(
                passed=True,
                rule_name=self.name,
                severity=GuardrailSeverity.INFO,
                message="Nessun dato strutturato da validare"
            )
        else:
            # Valida ogni JSON trovato
            for json_str in json_matches:
                is_valid, message, metadata = self.validate_json_structure(json_str)
                if not is_valid:
                    result = GuardrailResult(
                        passed=False,
                        rule_name=self.name,
                        severity=self.severity,
                        message=message,
                        metadata=metadata
                    )
                    break # interrompe l'esecuzione
            else:
                result = GuardrailResult(
                    passed=True,
                    rule_name=self.name,
                    severity=GuardrailSeverity.INFO,
                    message="Tutti i dati strutturati sono validi"
                )

        self._log_activation(result)
        return result

# Sistema completo con guardrails per API e risorse
def esempio_guardrails_api_e_risorse():
    """
    Esempio che mostra guardrails per API e gestione risorse
    """
    print("=== ESEMPIO GUARDRAILS API E RISORSE ===\n")

    # Configurazione sistema
    engine = GuardrailEngine()

    # Guardrail per controllo API
    api_guard = APICallGuardrail(
        allowed_domains={'api.github.com', 'httpbin.org', 'jsonplaceholder.typicode.com'},
        max_calls_per_minute=3,
        timeout_seconds=5
    )

    # Guardrail per risorse
    resource_guard = ResourceUsageGuardrail(
        max_memory_mb=200,
        max_execution_time_seconds=10
    )

    # Guardrail per validazione dati
    data_guard = DataValidationGuardrail(
        required_fields=['name', 'type'],
        field_types={'name': str, 'type': str, 'count': int},
        max_nesting_level=3
    )

    engine.add_input_guardrail(api_guard)
    engine.add_output_guardrail(resource_guard)
    engine.add_output_guardrail(data_guard)

    # Inizia monitoraggio risorse
    resource_guard.start_monitoring()

    # Test cases
    test_cases = [
        {
            "description": "URL permesso",
            "content": "Voglio chiamare https://api.github.com/users/octocat",
            "type": "input"
        },
        {
            "description": "URL non permesso",
            "content": "Chiamiamo https://malicious-site.com/api/data",
            "type": "input"
        },
        {
            "description": "JSON valido",
            "content": 'Ecco i dati: {"name": "test", "type": "example", "count": 42}',
            "type": "output"
        },
        {
            "description": "JSON non valido",
            "content": 'Dati: {"name": "test", "missing_required_field": true}',
            "type": "output"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- TEST {i}: {test_case['description']} ---")
        print(f"Contenuto: {test_case['content']}")

        if test_case['type'] == 'input':
            passed, modified, results = engine.validate_input(test_case['content'])
        else:
            passed, modified, results = engine.validate_output(test_case['content'])

        print(f"Validazione: {'✅ PASSED' if passed else '❌ FAILED'}")

        if modified != test_case['content']:
            print(f"Contenuto modificato: {modified}")

        # Mostra dettagli dei guardrails attivati
        for result in results:
            if not result.passed or result.severity != GuardrailSeverity.INFO:
                print(f"  {result.rule_name}: {result.message}")
                if result.metadata:
                    print(f"Metadata: {result.metadata}")

        print("-" * 60)

        # Simula del tempo di elaborazione
        time.sleep(0.5)

    # Statistiche finali con focus su API e risorse
    print("\n=== STATISTICHE API E RISORSE ===")
    stats = engine.get_statistics()

    # Aggiunge statistiche specifiche
    stats["api_stats"] = {
        "total_api_calls_tracked": len(api_guard.call_history),
        "allowed_domains": list(api_guard.allowed_domains),
        "rate_limit_per_minute": api_guard.max_calls_per_minute
    }

    stats["resource_stats"] = {
        "current_memory_mb": resource_guard.check_memory_usage(),
        "total_execution_time": resource_guard.check_execution_time(),
        "limits": {
            "max_memory_mb": resource_guard.max_memory_mb,
            "max_execution_time_seconds": resource_guard.max_execution_time_seconds
        }
    }

    print(json.dumps(stats, indent=2, default=str))

if __name__ == "__main__":
    esempio_guardrails_api_e_risorse()
```

## Best Practices

### 1. Progettazione dei Guardrails

- **Principio della Responsabilità Singola**: Ogni guardrail dovrebbe avere una responsabilità specifica
- **Composabilità**: I guardrails dovrebbero essere componibili e riutilizzabili
- **Configurabilità**: Parametri e soglie dovrebbero essere configurabili
- **Graceful Degradation**: In caso di errore, il sistema dovrebbe degradare elegantemente

### 2. Performance e Scalabilità

- **Ottimizzazione**: I guardrails devono essere efficienti per non impattare le performance
- **Caching**: Utilizzare cache per risultati frequenti (es. validazione domini)
- **Batching**: Processare multiple validazioni insieme quando possibile
- **Async Processing**: Considerare elaborazione asincrona per controlli non critici

### 3. Sicurezza

- **Defense in Depth**: Implementare più livelli di controllo
- **Fail Secure**: In caso di dubbio, fallire in modo sicuro
- **Logging Sicuro**: Non loggare informazioni sensibili
- **Audit Trail**: Mantenere traccia completa delle attivazioni

### 4. Monitoraggio e Manutenzione

- **Metriche**: Raccogliere metriche su attivazioni e performance
- **Alerting**: Configurare alert per violazioni critiche
- **Regular Review**: Rivedere regolarmente efficacia e configurazione
- **False Positive Analysis**: Analizzare e ridurre i falsi positivi

## Monitoraggio e Debugging

### Sistema di Monitoring Avanzato

```python
class GuardrailMonitor:
    """
    Sistema di monitoraggio per guardrails
    """
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.performance_data = []

    def record_guardrail_activation(self, guardrail_name: str, result: GuardrailResult, execution_time_ms: float):
        """
        Registra l'attivazione di un guardrail con metriche
        """
        if guardrail_name not in self.metrics:
            self.metrics[guardrail_name] = {
                'total_activations': 0,
                'passed': 0,
                'failed': 0,
                'avg_execution_time_ms': 0.0,
                'severity_counts': {}
            }

        metric = self.metrics[guardrail_name]
        metric['total_activations'] += 1

        if result.passed:
            metric['passed'] += 1 # aggiunge al dizionario metrics la chiave "passed" con valore aumentato di 1
        else:
            metric['failed'] += 1 # aggiiunge al dizionario metrics la chiave "failed" con valore aumentato di 1

            # Genera alert per fallimenti critici
            if result.severity == GuardrailSeverity.CRITICAL:
                self.alerts.append({
                    'timestamp': datetime.now(),
                    'guardrail': guardrail_name,
                    'message': result.message,
                    'severity': 'CRITICAL'
                })

        # Aggiorna tempo di esecuzione medio
        # Aggiunge al dizionario metric ulteriori chiavi con i rispettivi valori
        current_avg = metric['avg_execution_time_ms']
        total_count = metric['total_activations']
        metric['avg_execution_time_ms'] = (
            (current_avg * (total_count - 1) + execution_time_ms) / total_count
        )

        # Conta severità
        severity_str = result.severity.value
        if severity_str not in metric['severity_counts']:
            metric['severity_counts'][severity_str] = 0
        metric['severity_counts'][severity_str] += 1

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Restituisce dati per dashboard di monitoraggio
        """
        return {
            'guardrails_overview': self.metrics,
            'recent_alerts': self.alerts[-10:],  # Ultimi 10 alert
            'system_health': self._calculate_system_health()
        }

    def _calculate_system_health(self) -> Dict[str, Any]:
        """
        Calcola la salute generale del sistema
        """
        total_activations = sum(m['total_activations'] for m in self.metrics.values())
        total_failures = sum(m['failed'] for m in self.metrics.values())

        failure_rate = total_failures / total_activations if total_activations > 0 else 0

        health_status = 'HEALTHY'
        if failure_rate > 0.5:
            health_status = 'CRITICAL'
        elif failure_rate > 0.2:
            health_status = 'WARNING'

        return {
            'status': health_status,
            'total_activations': total_activations,
            'failure_rate': failure_rate,
            'critical_alerts_count': len([a for a in self.alerts if a['severity'] == 'CRITICAL'])
        }

# Esempio di integrazione con il monitoring
monitor = GuardrailMonitor()

# ... codice per testare il sistema completo ...
```

## Conclusioni

I guardrails rappresentano un componente fondamentale per la creazione di sistemi di Agentic AI sicuri, affidabili e controllabili. L'implementazione deve bilanciare:

- **Sicurezza** vs **Funzionalità**
- **Controllo** vs **Flessibilità**
- **Performance** vs **Completezza dei controlli**

La chiave del successo è:

1. **Progettazione modulare** che permetta facilità di manutenzione e estensione
2. **Monitoraggio continuo** per ottimizzare efficacia e ridurre falsi positivi
3. **Configurabilità** per adattarsi a diversi contesti e requisiti
4. **Trasparenza** per permettere debugging e audit

Con questi principi e gli esempi forniti, hai una base solida per implementare guardrails efficaci nei tuoi sistemi di Agentic AI.
