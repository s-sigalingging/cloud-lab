from flask import Flask, render_init_string, request, jsonify, redirect, url_for
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
<!DOCTYPE html>
<html>
<head>
    <title>Banking Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="card shadow-sm mx-auto" style="max-width: 600px;">
            <div class="card-header bg-dark text-white d-flex justify-content-between align-content-center">
                <h4 class="mb-0">Banking</h4>
                <span class="badge bg-success align-self-center">Live Cluster Sync</span>
            </div>
            <div class="card-body text-center p-4">
                <p class="text-muted text-uppercase small mb-1">Secure Account ID</p>
                <h5 class="text-secondary mb-4">{{ account_id }}</h5>
                <h1 class="display-4 text-dark fw-bold mb-4">${{ "%.2f"|format(balance) }}</h1>
                
                <hr class="my-4">
                
                <form action="/transfer" method="POST" class="text-start">
                    <label class="form-label text-muted small">Execute Instant Money Transfer</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" step="0.01" name="amount" class="form-control" placeholder="0.00" required>
                        <button class="btn btn-primary" type="submit">Send Authorization</button>
                    </div>
                </form>
            </div>
            <div class="card-footer bg-white text-muted text-center small py-3">
                Served by Cluster Node Host: <span class="font-monospace fw-bold">{{ hostname }}</span>
            </div>
        </div>
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

    return render_init_string(HTML_TEMPLATE, account_id=DEFAULT_ACCOUNT, balance=balance, hostname=hostname)

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