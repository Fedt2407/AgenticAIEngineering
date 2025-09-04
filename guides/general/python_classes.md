# Guida alle Classi Python per Agentic AI

## 1. Concetti Base delle Classi

### Esempio 1: Classe Base Semplice

```python
# Definizione di una classe base chiamata Persona
class Persona:
    # Metodo costruttore che viene chiamato quando creiamo un'istanza
    def __init__(self, nome, eta):
        # self si riferisce all'istanza corrente della classe
        # Assegniamo i parametri alle proprietà dell'istanza
        self.nome = nome  # Proprietà nome dell'istanza
        self.eta = eta    # Proprietà età dell'istanza

    # Metodo per far parlare la persona
    def parla(self):
        # Restituisce una stringa usando le proprietà dell'istanza
        return f"Ciao, sono {self.nome} e ho {self.eta} anni"

# Creazione di un'istanza della classe Persona
# Il costruttore __init__ viene chiamato automaticamente
persona1 = Persona("Mario", 30)

# Chiamata al metodo parla() sull'istanza
print(persona1.parla())  # Output: Ciao, sono Mario e ho 30 anni
```

## 2. Proprietà e Metodi Avanzati

### Esempio 2: Classe con Proprietà Private e Metodi di Validazione

```python
# Classe più avanzata con validazione dei dati
class ContoBancario:
    # Metodo costruttore con validazione
    def __init__(self, proprietario, saldo_iniziale=0):
        # Assegnazione del proprietario come proprietà pubblica accessibile direttamente
        # Il nome del proprietario del conto viene memorizzato senza restrizioni di accesso
        self.proprietario = proprietario

        # Inizializzazione del saldo come proprietà "privata" (con underscore)
        # In Python l'underscore è una convenzione che indica che questa proprietà
        # non dovrebbe essere acceduta direttamente dall'esterno della classe
        self._saldo = 0

        # Utilizzo del metodo deposita() per impostare il saldo iniziale
        # Questo garantisce che venga eseguita la validazione dell'importo
        # e che il saldo venga aggiornato in modo sicuro
        # L'inizializzazione dell'importo avrà il valore di default = 0
        self.deposita(saldo_iniziale)

    # Metodo per depositare denaro con validazione
    def deposita(self, importo):
        # Controllo che l'importo sia positivo
        if importo > 0:
            # Aggiunta dell'importo al saldo esistente
            self._saldo += importo
            # Messaggio di conferma
            print(f"Depositati {importo}€. Saldo attuale: {self._saldo}€")
        else:
            # Messaggio di errore per importo non valido
            print("L'importo deve essere positivo")

    # Metodo per prelevare denaro con controlli
    def preleva(self, importo):
        # Controllo che l'importo sia positivo e che ci siano fondi sufficienti
        if importo > 0 and importo <= self._saldo:
            # Sottrazione dell'importo dal saldo
            self._saldo -= importo
            print(f"Prelevati {importo}€. Saldo rimanente: {self._saldo}€")
        else:
            # Messaggio di errore
            print("Importo non valido o fondi insufficienti")

    # Metodo per ottenere il saldo (getter)
    def get_saldo(self):
        # Restituisce il saldo corrente
        return self._saldo

# Creazione di un'istanza del conto bancario
conto = ContoBancario("Alice", 100)

# Test dei metodi
conto.deposita(50)   # Deposito valido
conto.preleva(30)    # Prelievo valido
conto.preleva(200)   # Prelievo non valido (fondi insufficienti)
print(f"Saldo finale: {conto.get_saldo()}€")
```

## 3. Ereditarietà

### Esempio 3: Classe Base e Classi Derivate

```python
# Classe base per tutti i veicoli
class Veicolo:
    # Costruttore della classe base
    def __init__(self, marca, modello, anno):
        # Inizializzazione delle proprietà comuni a tutti i veicoli
        self.marca = marca
        self.modello = modello
        self.anno = anno
        # Stato del motore (spento di default)
        self.acceso = False

    # Metodo per accendere il veicolo
    def accendi(self):
        # Controlla se il veicolo è già acceso
        if not self.acceso:
            # Cambia lo stato a acceso
            self.acceso = True
            print(f"{self.marca} {self.modello} è stato acceso")
        else:
            print("Il veicolo è già acceso")

    # Metodo per spegnere il veicolo
    def spegni(self):
        # Controlla se il veicolo è acceso
        if self.acceso:
            # Cambia lo stato a spento
            self.acceso = False
            print(f"{self.marca} {self.modello} è stato spento")
        else:
            print("Il veicolo è già spento")

# Classe derivata da Veicolo
class Auto(Veicolo):
    # Costruttore della classe derivata
    def __init__(self, marca, modello, anno, num_porte):
        # Chiamata al costruttore della classe base
        super().__init__(marca, modello, anno)
        # Proprietà specifica delle auto
        self.num_porte = num_porte

    # Metodo specifico per le auto
    def suona_clacson(self):
        # Controlla se l'auto è accesa prima di suonare
        if self.acceso:
            print("BEEP BEEP!")
        else:
            print("Accendi l'auto prima di suonare il clacson")

# Classe derivata da Veicolo
class Moto(Veicolo):
    # Costruttore della classe derivata
    def __init__(self, marca, modello, anno, cilindrata):
        # Chiamata al costruttore della classe base
        super().__init__(marca, modello, anno)
        # Proprietà specifica delle moto
        self.cilindrata = cilindrata

    # Metodo specifico per le moto
    def impennata(self):
        # Controlla se la moto è accesa
        if self.acceso:
            print("Impennata spettacolare!")
        else:
            print("Accendi la moto per fare l'impennata")

# Creazione di istanze delle classi derivate
auto = Auto("Toyota", "Corolla", 2020, 4)
moto = Moto("Yamaha", "R1", 2021, 1000)

# Test dei metodi ereditati e specifici
auto.accendi()          # Metodo ereditato da Veicolo
auto.suona_clacson()    # Metodo specifico di Auto
moto.accendi()          # Metodo ereditato da Veicolo
moto.impennata()        # Metodo specifico di Moto
```

## 4. Classi per Agentic AI - Esempio Base

### Esempio 4: Sistema di Agenti Semplice

```python
# Enumerazione per i tipi di messaggio (simulata con una classe)
class TipoMessaggio:
    """
    Questa classe simula un'enumerazione per definire i tipi di messaggi possibili nel sistema.
    In Python moderno si potrebbe usare enum.Enum, ma questa è una versione semplificata
    che usa stringhe come costanti per maggiore leggibilità.
    """

    # Rappresenta una richiesta da un agente a un altro
    # Es: "Per favore calcola X" o "Hai nuove informazioni?"
    RICHIESTA = "richiesta"

    # Rappresenta una risposta a una richiesta precedente
    # Es: "Il risultato è Y" o "Ecco le nuove info"
    RISPOSTA = "risposta"

    # Rappresenta un messaggio di errore quando qualcosa va storto
    # Es: "Operazione non permessa" o "Dati non validi"
    ERRORE = "errore"

# Classe per rappresentare un messaggio tra agenti
class Messaggio:
    # Costruttore del messaggio
    def __init__(self, mittente, destinatario, contenuto, tipo=TipoMessaggio.RICHIESTA):
        # Chi invia il messaggio
        self.mittente = mittente
        # Chi riceve il messaggio
        self.destinatario = destinatario
        # Il contenuto del messaggio
        self.contenuto = contenuto
        # Il tipo di messaggio
        self.tipo = tipo
        # Timestamp del messaggio (simulato)
        # Il timestamp non è un parametro del costruttore perché viene generato
        # automaticamente quando viene creato il messaggio, non ha senso
        # permettere all'utente di specificarlo manualmente dato che rappresenta
        # il momento esatto di creazione del messaggio
        self.timestamp = "2024-01-01 10:00:00"

    # Rappresentazione del messaggio come stringa
    def __str__(self):
        return f"[{self.tipo.upper()}] Da {self.mittente} a {self.destinatario}: {self.contenuto}"

# Classe base per tutti gli agenti
class Agente:
    # Costruttore dell'agente
    # REMINDER: i parametri sono solo quelli che possono assere modificati (personalizzati) quando la classe viene chiamata
    # Es. la classe "Persona" definita inizialmente dove "nome" ed "età" sono specifici
    # Gli elementi che non devono essere passati quando viene chimata la classe non devono essere tra i parametri (in questo caso "messaggi_ricevuti" e "attivo")
    def __init__(self, nome, competenze=[]):
        # Nome identificativo dell'agente
        self.nome = nome
        # Lista delle competenze dell'agente
        self.competenze = competenze.copy()  # Copia per evitare riferimenti condivisi

        # Lista dei messaggi ricevuti - non è un parametro del costruttore perché
        # ogni agente deve partire con una lista vuota di messaggi, non avrebbe
        # senso permettere di inizializzarlo con messaggi già presenti
        self.messaggi_ricevuti = []
        # Stato dell'agente - non è un parametro perché ogni agente deve essere
        # creato attivo di default. Lo stato può essere modificato in seguito
        # attraverso metodi dedicati, ma all'inizio deve sempre essere True
        self.attivo = True

    # Metodo per ricevere un messaggio
    def ricevi_messaggio(self, messaggio):
        # Controlla se l'agente è attivo
        if self.attivo:
            # Aggiunge il messaggio alla lista
            self.messaggi_ricevuti.append(messaggio)
            print(f"{self.nome} ha ricevuto: {messaggio}")
            # Elabora il messaggio
            return self.elabora_messaggio(messaggio)
        else:
            print(f"{self.nome} è inattivo e non può ricevere messaggi")
            return None

    # Metodo base per elaborare i messaggi (da sovrascrivere nelle classi derivate)
    def elabora_messaggio(self, messaggio):
        # Implementazione base generica
        # Nota: messaggio.contenuto e messaggio.mittente sono attributi della classe messaggio definita più sopra
        risposta_contenuto = f"Ho ricevuto la tua richiesta: {messaggio.contenuto}"
        # Crea un messaggio di risposta
        # self.nome viene usato per accedere al nome dell'agente corrente che sta creando il messaggio.
        # self si riferisce all'istanza specifica dell'agente, quindi self.nome è il nome di questo
        # particolare agente che sarà il mittente del messaggio di risposta
        risposta = Messaggio(self.nome, messaggio.mittente, risposta_contenuto, TipoMessaggio.RISPOSTA)
        return risposta

    # Metodo per verificare se l'agente può gestire una competenza
    def puo_gestire(self, competenza):
        # Controlla se la competenza è nella lista delle competenze dell'agente
        # Fa una verifica nella lista delle competenze e restituisce un valore boolean
        return competenza in self.competenze

# Classe per un agente specializzato nel calcolo
class AgenteCalcolo(Agente):
    # Costruttore che inizializza l'agente con competenze di calcolo
    def __init__(self, nome):
        # Chiamata al costruttore della classe base con competenze specifiche
        # Chiama il costruttore della classe base (Agente) passando il nome ricevuto come parametro
        # e una lista delle competenze specifiche di questo agente specializzato in calcoli matematici
        super().__init__(nome, ["matematica", "calcolo", "algebra"])

    # Sovrascrive il metodo di elaborazione per operazioni matematiche
    def elabora_messaggio(self, messaggio):
        # Estrae il contenuto del messaggio
        richiesta = messaggio.contenuto.lower()

        # Controlla se è una richiesta di calcolo
        if "calcola" in richiesta or "+" in richiesta or "-" in richiesta:
            try:
                # Prova a eseguire operazioni matematiche semplici
                if "+" in richiesta:
                    # Estrae i numeri dalla richiesta (implementazione semplificata)
                    parti = richiesta.split("+")
                    if len(parti) == 2:
                        num1 = float(parti[0].strip())
                        num2 = float(parti[1].strip())
                        risultato = num1 + num2
                        contenuto_risposta = f"Il risultato di {num1} + {num2} è {risultato}"
                    else:
                        contenuto_risposta = "Formato non valido per l'addizione"
                else:
                    # Per altre operazioni, risposta generica
                    contenuto_risposta = "Posso aiutarti con calcoli matematici"
            except ValueError:
                # Gestione errori di conversione
                contenuto_risposta = "Errore nel parsing dei numeri"
        else:
            # Se non è una richiesta di calcolo, usa il metodo della classe base
            return super().elabora_messaggio(messaggio)

        # Crea e restituisce il messaggio di risposta
        risposta = Messaggio(self.nome, messaggio.mittente, contenuto_risposta, TipoMessaggio.RISPOSTA)
        return risposta

# Test del sistema di agenti
print("=== Test Sistema Agenti Base ===")

# Creazione degli agenti
# Creazione di un agente generico con competenza "generale"
# - Primo parametro: nome dell'agente ("AssistentePrincipale")
# - Secondo parametro: lista delle competenze (["generale"])
agente_generico = Agente("AssistentePrincipale", ["generale"])

# Creazione di un agente specializzato in calcoli matematici
# - Richiede solo il nome dell'agente ("CalcolatoreAI") come parametro
# - Le competenze (matematica, calcolo, algebra) sono predefinite nel costruttore della classe
agente_matematico = AgenteCalcolo("CalcolatoreAI")

# Creazione di messaggi di test

# Primo messaggio per l'agente CalcolatoreAI
# - mittente: "Utente" (chi invia il messaggio)
# - destinatario: "CalcolatoreAI" (l'agente che riceverà il messaggio)
# - contenuto: "Calcola 15 + 25" (richiesta di calcolo matematico che l'agente dovrà elaborare)
messaggio1 = Messaggio("Utente", "CalcolatoreAI", "Calcola 15 + 25")

# Secondo messaggio per l'agente generico
# - mittente: "Utente" (chi invia il messaggio)
# - destinatario: "AssistentePrincipale" (l'agente generico che riceverà il messaggio)
# - contenuto: "Come stai oggi?" (una domanda generica che non richiede calcoli)
messaggio2 = Messaggio("Utente", "AssistentePrincipale", "Come stai oggi?")

# Test dell'elaborazione dei messaggi
# Elaborazione dei messaggi chiamando il metodo ricevi_messaggio() della classe Agente
# che gestisce la ricezione e l'elaborazione del messaggio restituendo una risposta
risposta1 = agente_matematico.ricevi_messaggio(messaggio1)
print(f"Risposta ricevuta: {risposta1}")

risposta2 = agente_generico.ricevi_messaggio(messaggio2)
print(f"Risposta ricevuta: {risposta2}")
```

## 5. Sistema di Handoff Avanzato

### Esempio 5: Handoff tra Agenti con Guardrails

```python
# Classe per gestire i guardrails (controlli di sicurezza).
# Si tratta della classe base che racchiude i parametri validi per tutti i Guardrail.
class Guardrail:
    # Costruttore del guardrail
    def __init__(self, nome, descrizione):
        # Nome del controllo di sicurezza
        self.nome = nome
        # Descrizione del controllo
        self.descrizione = descrizione
        # Contatore delle violazioni (non viene passato come parametro in quanto quando la classe viene istanziata sarà a zero)
        self.violazioni = 0

    # Metodo base che verrà sovrascritto (override) dalle classi derivate
    # Questo è un esempio di polimorfismo - ogni classe derivata può implementare
    # il proprio comportamento specifico mantenendo la stessa interfaccia
    def controlla(self, messaggio):
        # Questa è l'implementazione di default nella classe base
        # Restituisce sempre True perché non effettua controlli reali
        # Le classi derivate (GuardrailLunghezza, GuardrailParoleVietate)
        # sovrascriveranno questo metodo con le proprie logiche di controllo
        # mantenendo la stessa firma del metodo (stesso nome e descrizione)
        return True, "Controllo base superato"

    # Metodo per registrare una violazione
    def registra_violazione(self):
        # Incrementa il contatore delle violazioni ogni volta che viene individuata una violazione
        self.violazioni += 1
        print(f"ATTENZIONE: Violazione del guardrail '{self.nome}' (#{self.violazioni})")

# Guardrail specifico per il controllo di lunghezza dei messaggi
class GuardrailLunghezza(Guardrail):
    # Costruttore con limite di lunghezza
    def __init__(self, lunghezza_max=100):
        # Chiamata al costruttore della classe base con nome e descrizione hardcoded: vedi super().__init__("LimiteLunghezza", f"Controlla che i messaggi...")
        # Non vengono passati come parametri perché questo guardrail ha uno scopo specifico
        # e quindi nome e descrizione sono predefiniti. A differenza della classe base Guardrail
        # che è generica e richiede questi parametri per essere flessibile, questa sottoclasse
        # implementa un controllo specifico sulla lunghezza e quindi ha un nome e una descrizione fissi
        # Nome e descrizione specifici sono definiti qui di seguito
        super().__init__("LimiteLunghezza", f"Controlla che i messaggi non superino {lunghezza_max} caratteri")
        # Limite massimo di caratteri
        self.lunghezza_max = lunghezza_max

    # Sovrascrive il metodo di controllo che nella classe base è definito di default come sempre superato
    def controlla(self, messaggio):
        # Controlla la lunghezza del contenuto del messaggio
        if len(messaggio.contenuto) > self.lunghezza_max:
            # Se supera il limite, registra violazione che incrementa di 1 il numero delle violazioni registrate
            self.registra_violazione()
            # Restituisce False e messaggio di errore
            return False, f"Messaggio troppo lungo: {len(messaggio.contenuto)} caratteri (max {self.lunghezza_max})"
        # Se è entro il limite, restituisce True
        return True, "Lunghezza accettabile"

# Guardrail per parole vietate
class GuardrailParoleVietate(Guardrail):
    # Costruttore con lista di parole vietate
    def __init__(self, parole_vietate=[]):
        # Chiamata al costruttore della classe base
        # Anche in questo caso i parametri della classe base (nome e descrizione) vengono hardcoded in quanto propri di questo specifico Guardrail
        super().__init__("ParoleVietate", "Controlla che il messaggio non contenga parole vietate")
        # Lista delle parole non permesse (in minuscolo per confronto)
        # Compone la lista delle parole vietate passate come parametro a questo specifico Guardrail
        self.parole_vietate = [parola.lower() for parola in parole_vietate]

    # Sovrascrive il metodo di controllo che nella classe base è definito di default come sempre superato
    def controlla(self, messaggio):
        # Converte il messaggio in minuscolo per il confronto
        contenuto_minuscolo = messaggio.contenuto.lower()

        # Controlla ogni parola vietata grazie ad un for loop che itera su ogni parola del messaggio (concertito in carattere minuscolo)
        for parola in self.parole_vietate:
            # Se trova una parola vietata
            if parola in contenuto_minuscolo:
                # Registra la violazione
                self.registra_violazione()
                # Restituisce False e messaggio di errore (si tratta di una tupla i cui valori verranno poi assegnati ai valori "valido" e "motivo")
                return False, f"Parola vietata trovata: '{parola}'"

        # Se non trova parole vietate, restituisce True
        return True, "Nessuna parola vietata trovata"

# Classe per gestire gli handoff tra agenti
class GestoreHandoff:
    # Costruttore del gestore
    # NOTA: questa classe non accetta parametri nel costruttore perché:
    # 1. È progettata per inizializzare strutture dati vuote che verranno popolate dopo
    #    attraverso metodi dedicati come registra_agente() e aggiungi_guardrail()
    # 2. Non ha bisogno di configurazione iniziale - il suo stato di partenza è sempre lo stesso
    #    con dizionari e liste vuote
    # 3. Segue il pattern di "costruzione graduale" dove gli elementi vengono aggiunti uno alla volta
    #    dopo la creazione dell'istanza, invece di essere passati tutti nel costruttore
    # 4. Questo approccio rende la classe più flessibile e riutilizzabile, dato che non richiede
    #    di conoscere tutti gli agenti e guardrails al momento della creazione
    def __init__(self):
        # Dizionario degli agenti registrati {nome: istanza_agente}
        self.agenti = {}
        # Lista dei guardrails attivi
        self.guardrails = []
        # Storico degli handoff
        self.storico_handoff = []

    # Metodo per registrare un agente
    def registra_agente(self, agente):
        # Aggiunge un nuovo elemento al dizionario self.agenti usando agente.nome come chiave
        # e l'oggetto agente stesso come valore. È equivalente a scrivere:
        # chiave = agente.nome
        # valore = agente
        #
        # Esempio di dizionario:
        # self.agenti = {
        #     "AgenteSupporto": <oggetto AgenteSupporto>,
        #     "AgenteVendite": <oggetto AgenteVendite>,
        #     "AgenteTecnico": <oggetto AgenteTecnico>
        # }
        self.agenti[agente.nome] = agente
        print(f"Agente '{agente.nome}' registrato con competenze: {agente.competenze}")

    # Metodo per aggiungere un guardrail alla lista definita nella classe generale
    def aggiungi_guardrail(self, guardrail):
        # Aggiunge il guardrail alla lista
        self.guardrails.append(guardrail)
        print(f"Guardrail '{guardrail.nome}' aggiunto al sistema")

    # Metodo per eseguire tutti i controlli di sicurezza
    def esegui_controlli(self, messaggio):
        # Itera su tutti i guardrails
        for guardrail in self.guardrails:
            # Esegue il controllo
            # Esempio di unpacking di tupla:
            # Se guardrail.controlla() restituisce (True, "OK")
            # allora valido = True e motivo = "OK"
            # L'unpacking della tupla funziona così:
            # 1. guardrail.controlla() restituisce una tupla con 2 elementi, es: (True, "OK")
            # 2. L'operatore = assegna il primo elemento della tupla alla prima variabile (valido)
            # 3. Il secondo elemento della tupla viene assegnato alla seconda variabile (motivo)
            # 4. Deve esserci lo stesso numero di variabili a sinistra dell'= e di elementi nella tupla
            valido, motivo = guardrail.controlla(messaggio)
            # Se il controllo fallisce
            if not valido:
                print(f"❌ Controllo fallito: {motivo}")
                # Restituisce False per bloccare l'elaborazione
                return False, motivo
            else:
                print(f"✅ {guardrail.nome}: {motivo}")

        # Se tutti i controlli sono passati
        return True, "Tutti i controlli superati"

    # Metodo per trovare l'agente più adatto per una competenza
    def trova_agente_per_competenza(self, competenza):
        # Itera su tutti gli agenti registrati
        for nome, agente in self.agenti.items():
            # Se l'agente può gestire la competenza e è attivo
            if agente.puo_gestire(competenza) and agente.attivo:
                # Restituisce il primo agente trovato
                return agente
        # Se nessun agente è trovato, restituisce None
        return None

    # Metodo per eseguire l'handoff
    def esegui_handoff(self, messaggio, competenza_richiesta):
        print(f"\n🔄 Iniziando handoff per competenza: '{competenza_richiesta}'")

        # Esegue i controlli di sicurezza
        # Anche in questo caso viene fatta l'unpacking della tupla
        controlli_ok, motivo = self.esegui_controlli(messaggio)
        if not controlli_ok:
            # Se i controlli falliscono, crea un messaggio di errore
            messaggio_errore = Messaggio("Sistema", messaggio.mittente, f"Richiesta bloccata: {motivo}", TipoMessaggio.ERRORE)
            return messaggio_errore

        # Trova l'agente appropriato
        agente_target = self.trova_agente_per_competenza(competenza_richiesta)

        # Se non trova un agente adatto
        if agente_target is None:
            print(f"❌ Nessun agente trovato per la competenza '{competenza_richiesta}'")
            messaggio_errore = Messaggio("Sistema", messaggio.mittente, f"Nessun agente disponibile per '{competenza_richiesta}'", TipoMessaggio.ERRORE)
            return messaggio_errore

        print(f"✅ Handoff a '{agente_target.nome}'")

        # Registra l'handoff nello storico
        record_handoff = {
            "mittente": messaggio.mittente,
            "agente": agente_target.nome,
            "competenza": competenza_richiesta,
            "timestamp": messaggio.timestamp
        }
        self.storico_handoff.append(record_handoff)

        # Invia il messaggio all'agente target
        risposta = agente_target.ricevi_messaggio(messaggio)

        print(f"📨 Risposta generata da '{agente_target.nome}'")
        return risposta

# Test completo del sistema con handoff e guardrails
print("\n" + "="*50)
print("TEST SISTEMA COMPLETO CON HANDOFF E GUARDRAILS")
print("="*50)

# Creazione del gestore handoff
gestore = GestoreHandoff()

# Creazione e registrazione degli agenti
agente_calc = AgenteCalcolo("MatematicoAI")
agente_generale = Agente("AssistenteGenerale", ["conversazione", "aiuto"])

gestore.registra_agente(agente_calc)
gestore.registra_agente(agente_generale)

# Creazione e aggiunta dei guardrails
guardrail_lunghezza = GuardrailLunghezza(50)  # Max 50 caratteri
guardrail_parole = GuardrailParoleVietate(["spam", "virus", "hack"])

gestore.aggiungi_guardrail(guardrail_lunghezza)
gestore.aggiungi_guardrail(guardrail_parole)

# Test 1: Messaggio valido con competenza matematica
print("\n--- Test 1: Richiesta matematica valida ---")
messaggio_math = Messaggio("Utente", "Sistema", "10 + 5", TipoMessaggio.RICHIESTA)
risposta1 = gestore.esegui_handoff(messaggio_math, "matematica")
print(f"Risultato: {risposta1}")

# Test 2: Messaggio troppo lungo (viola guardrail)
print("\n--- Test 2: Messaggio troppo lungo ---")
messaggio_lungo = Messaggio("Utente", "Sistema", "Questo è un messaggio molto lungo che supera il limite di caratteri stabilito dal guardrail", TipoMessaggio.RICHIESTA)
risposta2 = gestore.esegui_handoff(messaggio_lungo, "generale")
print(f"Risultato: {risposta2}")

# Test 3: Messaggio con parola vietata
print("\n--- Test 3: Messaggio con parola vietata ---")
messaggio_spam = Messaggio("Utente", "Sistema", "Aiuto con spam", TipoMessaggio.RICHIESTA)
risposta3 = gestore.esegui_handoff(messaggio_spam, "generale")
print(f"Risultato: {risposta3}")

# Test 4: Competenza non disponibile
print("\n--- Test 4: Competenza non disponibile ---")
messaggio_sconosciuto = Messaggio("Utente", "Sistema", "Ciao", TipoMessaggio.RICHIESTA)
risposta4 = gestore.esegui_handoff(messaggio_sconosciuto, "cucina")
print(f"Risultato: {risposta4}")

# Visualizzazione dello storico
print(f"\n--- Storico Handoff ---")
# Output esempio:
# 1. Utente -> MatematicoAI per 'matematica'
# 2. Utente -> AssistenteGenerale per 'generale'
# 3. Utente -> AssistenteGenerale per 'generale'
# 4. Utente -> Sistema per 'cucina'
for i, record in enumerate(gestore.storico_handoff, 1):
    print(f"{i}. {record['mittente']} -> {record['agente']} per '{record['competenza']}'")

# Statistiche guardrails
print(f"\n--- Statistiche Guardrails ---")
for guardrail in gestore.guardrails:
    print(f"{guardrail.nome}: {guardrail.violazioni} violazioni")
```

## Conclusione

Questa guida ti ha mostrato come le classi Python vengono utilizzate per costruire sistemi di AI agentiva:

1. **Classi Base**: Per definire entità comuni (Agente, Messaggio)
2. **Ereditarietà**: Per specializzare agenti con competenze specifiche
3. **Encapsulation**: Per proteggere dati sensibili e garantire controlli
4. **Polimorfismo**: Per gestire diversi tipi di agenti con interfacce comuni
5. **Composizione**: Per costruire sistemi complessi combinando oggetti semplici

I concetti mostrati sono fondamentali per comprendere architetture più complesse di AI agentiva, dove gli handoff e i guardrails garantiscono un funzionamento sicuro e controllato del sistema.
