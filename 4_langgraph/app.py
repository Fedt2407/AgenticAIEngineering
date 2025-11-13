import gradio as gr
from sidekick import Sidekick


async def setup():
    sidekick = Sidekick()
    await sidekick.setup()
    return sidekick

async def process_message(sidekick, message, success_criteria, history):
    # Qui viene lanciata la funzione (coroutine) .run_superstep sull'oggetto sidekick 
    # che abbiamo instanziato con la classe Sidekick() definita nel file sidekick ed importata in questo file
    results = await sidekick.run_superstep(message, success_criteria, history)
    return results, sidekick
    
async def reset():
    new_sidekick = Sidekick()
    await new_sidekick.setup()
    return "", "", None, new_sidekick

def free_resources(sidekick):
    print("Cleaning up")
    try:
        if sidekick:
            sidekick.free_resources()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


with gr.Blocks(title="Sidekick", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Sidekick Personal Co-Worker")

    # È importante usare lo State per permettere a più utenti di usare l'applicazione contemporaneamente
    # In questo modo si evita il rischio che più utenti condividano le stesse variabili
    sidekick = gr.State(delete_callback=free_resources)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the Sidekick")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")
  

    # Queste sono le funzioni di callback
    # Il blocco di codice soprastante gestisce le funzionalità di frontend mentre
    # Le funzioni callback gestiscono le attività di backend
    # NOTA: queste funzioni di callback prendono una lista di parametri in input e ritornano un output con i parametri della seconda lista
    ui.load(setup, [], [sidekick])  # Questa funzione serve a laciare una nuova sessione della nostra app ad ogni chiamata (es. se ci sono più utenti in contemporanea)
    message.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    success_criteria.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    # Quando clicchiamo sul pulsante viene lanciata la funzione "process_message" che prende gli input della prima lista e ritorna un output della seconda lista
    go_button.click(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    reset_button.click(reset, [], [message, success_criteria, chatbot, sidekick])

    
ui.launch(inbrowser=True)