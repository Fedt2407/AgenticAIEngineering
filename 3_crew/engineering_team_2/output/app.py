import gradio as gr
from accounts import Account, get_share_price

# Global account instance
account = None

def create_account(account_id, initial_deposit):
    global account
    try:
        initial_deposit = float(initial_deposit)
        if initial_deposit <= 0:
            # This function returns 5 values that correspond to different UI elements:
            # 1. Status message ("Initial deposit must be positive")
            # 2. Account info (empty string when account creation fails)
            # 3. Holdings info (empty string when account creation fails) 
            # 4. Profit/Loss info (empty string when account creation fails)
            # 5. Transactions info (empty string when account creation fails)
            return "Initial deposit must be positive", "", "", "", ""
        
        account = Account(account_id, initial_deposit)
        # Return success message and the results of the 4 functions that display account status
        return f"Account created successfully with ID: {account_id}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()
    except Exception as e:
        return f"Error creating account: {str(e)}", "", "", "", ""

def deposit_funds(amount):
    global account
    if account is None:
        return "Please create an account first", "", "", "", ""
    
    try:
        amount = float(amount)
        # The deposit() method is defined in the Account class in accounts.py
        # It adds the specified amount to the account balance
        # It takes a float parameter 'amount' representing the money to deposit
        # The method will raise an exception if amount is negative or zero
        account.deposit(amount)
        return "Deposit successful", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()
    except Exception as e:
        return f"Error: {str(e)}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()

def withdraw_funds(amount):
    global account
    if account is None:
        return "Please create an account first", "", "", "", ""
    
    try:
        amount = float(amount)
        account.withdraw(amount)
        return "Withdrawal successful", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()
    except Exception as e:
        return f"Error: {str(e)}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()

def buy_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first", "", "", "", ""
    
    try:
        quantity = int(quantity)
        account.buy_shares(symbol.upper(), quantity)
        return f"Purchase successful: {quantity} shares of {symbol.upper()}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()
    except Exception as e:
        return f"Error: {str(e)}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()

def sell_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first", "", "", "", ""
    
    try:
        quantity = int(quantity)
        account.sell_shares(symbol.upper(), quantity)
        return f"Sale successful: {quantity} shares of {symbol.upper()}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()
    except Exception as e:
        return f"Error: {str(e)}", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()

def get_account_info():
    global account
    if account is None:
        return ""
    
    portfolio_value = account.calculate_portfolio_value()
    return f"Account ID: {account.account_id}\nBalance: ${account.balance:.2f}\nPortfolio Value: ${portfolio_value:.2f}"

def get_holdings():
    global account
    if account is None:
        return ""
    
    holdings = account.list_holdings()
    if not holdings:
        return "No holdings"
    
    holdings_text = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        holdings_text += f"{symbol}: {quantity} shares @ ${price:.2f} each = ${value:.2f}\n"
    return holdings_text

def get_profit_loss():
    global account
    if account is None:
        return ""
    
    pnl = account.report_profit_or_loss()
    return f"Profit/Loss: ${pnl:.2f}"

def get_transactions():
    global account
    if account is None:
        return ""
    
    transactions = account.list_transactions()
    return "Transaction History:\n" + "\n".join(transactions)

def refresh_display():
    global account
    if account is None:
        return "Please create an account first", "", "", "", ""
    
    return "Display refreshed", get_account_info(), get_holdings(), get_profit_loss(), get_transactions()

with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("Simple account management system for trading simulation")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Account Management")
            account_id = gr.Textbox(label="Account ID", placeholder="Enter account ID")
            initial_deposit = gr.Number(label="Initial Deposit", value=1000.0)
            create_btn = gr.Button("Create Account")
            
            gr.Markdown("## Funds Management")
            deposit_amount = gr.Number(label="Deposit Amount", value=100.0)
            deposit_btn = gr.Button("Deposit Funds")
            withdraw_amount = gr.Number(label="Withdraw Amount", value=50.0)
            withdraw_btn = gr.Button("Withdraw Funds")
            
            gr.Markdown("## Trading")
            symbol = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Stock Symbol")
            quantity = gr.Number(label="Quantity", value=1, precision=0)
            buy_btn = gr.Button("Buy Shares")
            sell_btn = gr.Button("Sell Shares")
            
            refresh_btn = gr.Button("Refresh Display")
        
        with gr.Column():
            gr.Markdown("## Account Information")
            status_output = gr.Textbox(label="Status", interactive=False)
            account_info = gr.Textbox(label="Account Details", interactive=False, lines=3)
            holdings_info = gr.Textbox(label="Holdings", interactive=False, lines=5)
            pnl_info = gr.Textbox(label="Profit/Loss", interactive=False)
            transactions_info = gr.Textbox(label="Transactions", interactive=False, lines=10)
    
    # Event handlers
    create_btn.click(
        create_account,
        inputs=[account_id, initial_deposit],
        outputs=[status_output, account_info, holdings_info, pnl_info, transactions_info]
    )
    
    deposit_btn.click(
        deposit_funds,
        inputs=[deposit_amount],
        outputs=[status_output, account_info, holdings_info, pnl_info, transactions_info]
    )
    
    withdraw_btn.click(
        withdraw_funds,
        inputs=[withdraw_amount],
        outputs=[status_output, account_info, holdings_info, pnl_info, transactions_info]
    )
    
    buy_btn.click(
        buy_shares,
        inputs=[symbol, quantity],
        outputs=[status_output, account_info, holdings_info, pnl_info, transactions_info]
    )
    
    sell_btn.click(
        sell_shares,
        inputs=[symbol, quantity],
        outputs=[status_output, account_info, holdings_info, pnl_info, transactions_info]
    )
    
    refresh_btn.click(
        refresh_display,
        outputs=[status_output, account_info, holdings_info, pnl_info, transactions_info]
    )

if __name__ == "__main__":
    demo.launch()