from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Environment location routing paths
SWITCH_URL = os.getenv("SWITCH_SERVICE_URL", "http://payment-switch-service:8081/api/v1/switch/process")
LEDGER_BALANCE_URL = os.getenv("LEDGER_BALANCE_URL", "http://core-ledger-service:8082/ledger/balance")

# Hardcoded standard dashboard user account for mock channel
DEFAULT_ACCOUNT = "ACC-771B0355"

# The HTML Template render engine string matching your previous dashboard dashboard layout
HTML_TEMPLATE = """
<html>
    <head>
        <title>Secure GCP Mobile Banking</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f6f9; }
            .card { background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; }
            h1 { color: #0A58CA; }
            .balance { font-size: 32px; color: #212529; font-weight: bold; margin: 20px 0; }
            .footer { color: #6c757d; font-size: 12px; margin-top: 20px; font-family: monospace; }
            .input-group { text-align: left; margin-bottom: 15px; }
            .input-group label { display: block; font-size: 12px; color: #6c757d; margin-bottom: 5px; font-weight: bold; }
            .input-group input { width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 5px; box-sizing: border-box; }
            .btn { background-color: #0D6EFD; color: white; border: none; padding: 12px; width: 100%; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 14px; }
            .btn:hover { background-color: #0b5ed7; }
        </style>
    </head>
    <body>
        <div class="card">
            <div style="background: #212529; color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px; display: inline-block; float: right; font-weight: bold;">Live Cluster Sync</div>
            <div style="clear: both;"></div>
            <p style="color: #6c757d; margin-bottom: 2px; font-size: 12px; font-weight: bold; letter-spacing: 0.5px;">SECURE ACCOUNT ID</p>
            <h3 style="margin-top: 0; color: #495057;">{{ account_id }}</h3>
            
            <div class="balance">${{ "%.2f"|format(balance) }}</div>
            
            <hr style="border: 0; border-top: 1px solid #dee2e6; margin: 20px 0;">
            
            <form action="/transfer" method="POST">
                <div class="input-group">
                    <label>DESTINATION ACCOUNT ID</label>
                    <input type="text" name="destination_account" placeholder="e.g., 111042 (Internal) or 999887 (External)" required>
                </div>
                <div class="input-group">
                    <label>EXECUTE INSTANT MONEY TRANSFER ($)</label>
                    <input type="number" step="0.01" name="amount" placeholder="0.00" required>
                </div>
                <button type="submit" class="btn">Send Authorization</button>
            </form>
            
            <hr style="border: 0; border-top: 1px solid #dee2e6; margin: 20px 0;">
            <div class="footer">Served by Cluster Node Host: {{ hostname }}</div>
        </div>
    </body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    import socket
    hostname = socket.gethostname()
    balance = 0.00

    # Reach out to Ledger network to fetch live account balance data
    try:
        response = requests.get(f"{LEDGER_BALANCE_URL}/{DEFAULT_ACCOUNT}", timeout=3)
        if response.status_code == 200:
            balance = response.json().get("balance", 0.00)
    except requests.exceptions.RequestException:
        logging.error("[FRONTEND CRITICAL] Could not query backend ledger for wallet balances.")

    return render_template_string(HTML_TEMPLATE, account_id=DEFAULT_ACCOUNT, balance=balance, hostname=hostname)

@app.route("/transfer", methods=["POST"])
def transfer():
    amount = request.form.get("amount")
    
    # Forward the money transaction transaction directly to the secure switch gate
    payload = {"account_id": DEFAULT_ACCOUNT, "amount": amount}
    try:
        requests.post(SWITCH_URL, json=payload, timeout=4)
    except requests.exceptions.RequestException as e:
        logging.error(f"[FRONTEND EXCEPTION] Transaction pipeline drop: {str(e)}")

    return redirect(url_for("index"))

if __name__ == "__main__":
    # Open face interface entry port
    app.run(host="0.0.0.0", port=8080)