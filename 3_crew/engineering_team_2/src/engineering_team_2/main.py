#!/usr/bin/env python
import sys
import warnings


from engineering_team_2.crew import EngineeringTeam2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


requirements = """
A simple account management system for a trading simulation platform.
The system should allow users to create an account, deposit funds and withdraw funds.
The system should allow users to record that they've bought or sold shares, providing a quantity.
The system should calculate the total value of the user's portfolio and the profit or loss of the initial deposit.
The system should be able to report the holdings of the user at any point in time.
The system should be able to report the profit or loss of the user at any point in time.
The system should be able to list the transactions that the user has made over time.
The system should prevent the user from withdrawing funds that that will leave them with a negative balance or
from buyiing more shares that they can afford selling shares that they don't have.
The system has access to a function get_shares-price(symbol) whiche return the current price of a share and 
include a test implementation that returns fixed prices for AAPL, TSLA, GOOGL.
"""

module_name = "accounts.py"

class_name = "Account"

# Main funcition
def run():
    """
    Run the crew.
    """

    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }
    
    try:
        result = EngineeringTeam2().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


