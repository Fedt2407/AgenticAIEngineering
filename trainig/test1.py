# with open("data.txt", "w") as file:
#     file.write("This is a test")

# with open("data.txt", "a") as file:
#     file.write("\n\nThis is a second line")

# with open("data.txt", "r") as file:
#     for line in file:
#         print(line.strip())

# import glob
# text_files = glob.glob("**/*.txt", recursive=True)
# print(text_files)

# from pathlib import Path
# import glob

# # Define input and output file paths using pathlib's Path object for cross-platform compatibility
# input_file = Path('data') / 'input.txt'  # Creates path to input.txt in 'data' directory
# output_file = Path('data') / 'output.txt'  # Creates path to output.txt in 'data' directory

# # Create the output directory if it doesn't exist, using mkdir with parents=True to create all needed directories
# output_file.parent.mkdir(parents=True, exist_ok=True)  # exist_ok=True prevents errors if directory already exists

# # Check if input file exists before processing
# if input_file.exists():
#     # Open both input and output files using context managers for automatic closing
#     with open(input_file, 'r', encoding='utf-8') as infile, \
#          open(output_file, 'w', encoding='utf-8') as outfile:
#         # Read input file line by line to handle large files efficiently
#         for line in infile:
#             # Convert each line to uppercase and write to output file
#             outfile.write(line.upper())  # Example: Write uppercase content
# else:
#     # Print error message if input file is not found
#     print(f"File {input_file} not found.")

# # Use glob to find all .txt files in the data directory
# # Find all .txt files in the data directory:
# # 1. Path('data') creates a Path object for the 'data' directory
# # 2. Path('data') / '*.txt' joins 'data' with '*.txt' to create 'data/*.txt' pattern
# # 3. str() converts the Path object to a string since glob.glob requires a string pattern
# # 4. glob.glob() returns a list of all files matching the pattern
# txt_files = glob.glob(str(Path('data') / '*.txt'))
# # Print the list of found text files
# # print("Text files in the 'data' directory:", txt_files)


# class Car:
#     def __init__(self, make, model, year):
#         self.make = make
#         self.model = model
#         self.year = year

#     def describe(self):
#         print(f"My car is a {self.make} {self.model} manufactured in {self.year} ")

#     def start(self):
#         print(f"{self.make} {self.model} engine is on")

# my_car = Car("BMW", "320d Coupé", "2008")

# print(my_car.make)
# my_car.describe()
# my_car.start()

from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv(override=True)

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if deepseek_api_key:
    print("DeepSeekAPI Key available")
if openai_api_key:
    print("OpenAI API Key available")

########################################################################
# In questo blocco di codice viene generata la domanda per tutti gli LLM
########################################################################

# Prompt per far generare una domanda a DeepSeek
question_prompt = """
Definisci una problematica attuale che potrebbe essere risolta in modo efficace utilizzanso un agente AI.
Non fornire nessuna risposta o indizio sulla soluzione.
"""

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
deepseek = OpenAI(api_key=deepseek_api_key, base_url=DEEPSEEK_BASE_URL)

# DeepSeek genera la domanda
messages = [{
        "role": "user",
        "content": question_prompt
    }]

question_response = deepseek.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

# Estraiamo la domanda generata
generated_question = question_response.choices[0].message.content
print("Domanda generata da DeepSeek:", generated_question)

#######################################################
# In questo blocco genereremeo le risposte dei vari LLM
#######################################################

request = f"Fornisci in 100 parole una possibile soluzione alla problematica: {generated_question}"

# Inizializzazione della classe dei modelli. NOTA: DeepSeek è già inizializzato nella formulazione della domanda
openai = OpenAI(api_key=openai_api_key)
ollama = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

models = {
    "deepseek": {"llm": deepseek, "model_name": "deepseek-chat"},
    "openai": {"llm": openai, "model_name": "gpt-4o-mini"},
    "ollama": {"llm": ollama, "model_name": "llama3.2"}
}

competitors = []
answers = []

# Tutti i modelli rispondono alla stessa domanda generata da DeepSeek
messages = [{
    "role": "user",
    "content": request
}]

# Itera in tutti i modelli per generare un risposta
for key, value in models.items():
    response = value["llm"].chat.completions.create(
        model=value["model_name"],
        messages=messages
    )

    competitors.append(key)
    answers.append(response.choices[0].message.content)

# Stampa i risultati delle risposte
# NOTA: zip() crea un iteratore di tuple dove ogni tupla contiene gli elementi i-esimi di ogni iterabile passato come argomento
# in questo caso crea coppie di (competitor, answer) dalle due liste competitors e answers
for competitor, answer in zip(competitors, answers):
    print(f"\n\nModello: {competitor.upper()}\n{answer}")

###################################################################
# In questo blocco verrà fatta la valutazione della miglir risposta
###################################################################

# Qui verrà creata un'unica risposta usando enumerate() per ottenere sia l'indice che l'elemento della lista answers
answers_together = ""
for index, anwer in enumerate(answers):
    answers_together += f"Answer from model {index + 1}\n" # usiamo +1 perché la sista è zero based
    answers_together += anwer + "\n\n"

judge = f"""Stai giudicando una competizione tra {len(competitors)} modelli.
A ciascun modello è stata posta questa problematica: {question_response}
Il tuo compito è valutare ogni risposta per chiarezza e forza argomentativa, e classificarle dalla migliore alla peggiore.
Rispondi con JSON, e solo JSON, con il seguente formato:
{{"rank_results": ["numero del miglior modello", "numero del secondo miglior modello", "numero del terzo miglior modello", ...]}}
Ecco le risposte di ogni modello: {answers_together}
Ora rispondi con il JSON contenente l'ordine di classifica dei modelli, nient'altro. Non includere formattazione markdown o blocchi di codice."""

judge_message = [{
    "role": "user",
    "content": judge
}]

judge_response = deepseek.chat.completions.create(
    model="deepseek-chat",
    messages=judge_message
)

rank_results = judge_response.choices[0].message.content
print(rank_results)

results_dict = json.loads(rank_results) # Parse the JSON string response into a Python dictionary
ranks = results_dict["rank_results"] # Extract the ranks from the dictionary
for index, result in enumerate(ranks): # Iterate through the ranks
    competitor = competitors[int(result)-1] # Get the competitor name from the list of competitors
    print(f"Rank {index+1}: {competitor}")

