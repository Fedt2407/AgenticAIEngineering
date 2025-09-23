#############################################################################
# Il progetto ha l'bbiettivo di creare un team completo di software engineers
#############################################################################

#!/usr/bin/env python
import sys
import warnings

from coder_2.crew import Coder2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Here we define the assignment to be asked to the coder agent
assignment = (
    "Write a python program to calculate the first 10,000 terms"
    "of this series, multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ..."
    )

def run():
    """
    Run the crew.
    """
    inputs = {
        'assignment': assignment,
    }
    
    try:
        result = Coder2().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         Coder2().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         Coder2().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }
    
#     try:
#         Coder2().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")
