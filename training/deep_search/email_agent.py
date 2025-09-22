#############################
# TOOL PER L'INVIO DELLA MAIL
#############################

import sendgrid
from sendgrid.helpers.mail import Email, Mail, To, Content
import os
from typing import Dict
from agents import Agent, function_tool

# Definiamo la funzione che verrà tradformata in tool
@function_tool
def send_mail(subject: str, html_body: str) -> Dict[str, str]:
    """Invia una email utilizzando l'API di SendGrid.
    
    Questa funzione invia una email formattata in HTML utilizzando il servizio SendGrid.
    Richiede una chiave API di SendGrid configurata nelle variabili d'ambiente.

    Args:
        subject (str): L'oggetto dell'email
        html_body (str): Il corpo dell'email in formato HTML

    Returns:
        Dict[str, str]: Un dizionario contenente lo stato dell'invio
        - "status": "success" se l'invio è andato a buon fine

    Note:
        - L'email viene inviata da federico.tognettigmail.com a federico.tognetti@gmail.com
        - È necessario che la chiave API di SendGrid sia impostata nella variabile d'ambiente SENDGRID_API_KEY
        - Il contenuto dell'email deve essere in formato HTML valido
    """
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("federico.tognettigmail.com")
    to_email = To("federico.tognetti@gmail.com")
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}


# Definiamo ora l'agente
email_agent_instructions = (
    "Sei in grado di inviare un'email HTML ben formattata basata su un report dettagliato."
    "Ti verrà fornito un report dettagliato. Dovrai utilizzare il tuo tool per inviare una email,"
    "fornendo il report convertito in HTML pulito e ben presentato con un oggetto appropriato."
)

email_agent = Agent(
    name="Email agent",
    instructions=email_agent_instructions,
    model="gpt-4o-mini",
    tools=[send_mail]
)