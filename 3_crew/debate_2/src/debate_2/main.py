#!/usr/bin/env python
import sys
import warnings

from debate_2.crew import Debate2 # importa la classe creata nel file crew.py della del progetto debate_2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    # Questa variabile specifica gli elementi del template che possiamo modificare quando lanciamo la fuinzione (in questo caso motion)
    inputs = {
        'motion': 'Ci dovrebbero essere regole stingenti per regolare l\'uso dell\'intelligenza artificilale',
    }
    
    try:
        result = Debate2().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'motion': 'Ci dovrebbero essere regole stingenti per regolare l\'uso dell\'intelligenza artificilale',
    }
    try:
        Debate2().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Debate2().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'motion': 'Ci dovrebbero essere regole stingenti per regolare l\'uso dell\'intelligenza artificilale',
    }
    
    try:
        Debate2().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
