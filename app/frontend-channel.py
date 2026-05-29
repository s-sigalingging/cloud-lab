from flask import Flask, render_template_string, request, redirect, url_for
import requests
import os
import logging
import socket

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

LEDGER_URL = os.getenv("LEDGER_SERVICE_URL", "http://core-ledger-service.app.svc.cluster.local:8082")
SWITCH_URL = os.getenv("SWITCH_SERVICE_URL", "http://payment-switch-service.app.svc.cluster.local:8081/api/v1/switch/process")
ONBOARDING_URL = os.getenv("ONBOARDING_SERVICE_URL", "http://onboarding.app.svc.cluster.local:8083/api/v1/onboard")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>S-Shield Neobank Secure Core</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; display: flex; gap: 20px; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); flex: 1; }
        h2 { color: #0A58CA; margin-top: 0; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
        .balance { font-size: 36px; color: #212529; font-weight: bold; margin: 15px 0; font-family: monospace; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; font-size: 11px; color: #6c757d; margin-bottom: 5px; font-weight: bold; letter-spacing: 0.5px; }
        .input-group input { width: 100%; padding: 12px; border: 1px solid #ced4da; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { background-color: #0D6EFD; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; }
        .btn-success { background-color: #198754; }
        .alert { padding: 12px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; font-weight: bold; }
        .alert-success { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }
        .alert-danger { background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }
        .footer { text-align: center; color: #6c757d; font-size: 11px; margin-top: 30px; font-family: monospace; }
    </style>
</head>
<body>
    <div style="text-align:center; margin-bottom: 30px;">
        <h1>🛡️ S-Shield Neobank Secure Terminal</h1>
    </div>

    <div class="container">
        {% if not authenticated %}
        <div class="card">
            <h2>Secure Portal Login</h2>
            {% if tx_msg %}
                <div class="alert alert-danger">{{ tx_msg }}</div>
            {% endif %}
            <form action="/login" method="POST">
                <div class="input-group">
                    <label>FULL LEGAL NAME</label>
                    <input type="text" name="login_name" placeholder="Enter registration name..." required>
                </div>
                <div class="input-group">
                    <label>4-DIGIT SECURITY PIN</label>
                    <input type="password" maxlength="4" name="login_pin" placeholder="****" required>
                </div>
                <button type="submit" class="btn">Verify Identity</button>
            </form>
        </div>

        <div class="card" style="border-top: 4px solid #198754;">
            <h2>Open Corporate Account</h2>
            {% if onboard_msg %}
                <div class="alert alert-success">{{ onboard_msg }}</div>
            {% endif %}
            <form action="/onboard" method="POST">
                <div class="input-group">
                    <label>FULL LEGAL NAME</label>
                    <input type="text" name="customer_name" placeholder="e.g., Bassura City" required>
                </div>
                <div class="input-group">
                    <label>INITIAL DEPOSIT ($)</label>
                    <input type="number" step="0.01" name="initial_deposit" placeholder="500.00" required>
                </div>
                <div class="input-group">
                    <label>CHOOSE A 4-DIGIT SECURITY PIN</label>
                    <input type="password" maxlength="4" name="customer_pin" placeholder="e.g., 1234" required>
                </div>
                <button type="submit" class="btn btn-success">Register Vault Profile</button>
            </form>
        </div>

        {% else %}
        <div class="card" style="border-top: 4px solid #0D6EFD;">
            <h2>Authorized Vault View</h2>
            {% if tx_msg %}
                <div class="alert alert-success">{{ tx_msg }}</div>
            {% endif %}
            <p style="color: #6c757d; font-size: 11px; margin-bottom: 2px;">WELCOME AUTHENTICATED CLIENT</p>
            <h3>{{ account_holder }}</h3>

            <p style="color: #6c757d; font-size: 11px; margin-bottom: 2px;">ACCOUNT ID</p>
            <h4 style="font-family: monospace; color: #0A58CA;">{{ account_id }}</h4>

            <p style="color: #6c757d; font-size: 11px; margin-bottom: 2px;">VERIFIED SYSTEM BALANCE</p>
            <div class="balance">${{ "%.2f"|format(balance) }}</div>
            
            <a href="/" style="display:inline-block; margin-top:15px; color:#dc3545; font-weight:bold; text-decoration:none;">🔒 Log Out</a>
        </div>

        <div class="card">
            <h2>Authorized Wire Transfer</h2>
            <form action="/transfer" method="POST">
                <input type="hidden" name="source_account" value="{{ account_id }}">
                <input type="hidden" name="authenticated_name" value="{{ account_holder }}">
                <input type="hidden" name="authenticated_balance" value="{{ balance }}">
                <div class="input-group">
                    <label>DESTINATION ACCOUNT ID</label>
                    <input type="text" name="destination_account" placeholder="e.g., 111002" required>
                </div>
                <div class="input-group">
                    <label>TRANSFER AMOUNT ($)</label>
                    <input type="number" step="0.01" name="amount" placeholder="0.00" required>
                </div>
                <button type="submit" class="btn">Authorize Core Wire Execution</button>
            </form>
        </div>
        {% endif %}
    </div>

    <div class="footer">
        Node: {{ hostname }} | Infrastructure Security: GKE Multi-Tier Isolated VPC Network
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    tx_msg = request.args.get("tx_msg")
    onboard_msg = request.args.get("onboard_msg")
    return render_template_string(HTML_TEMPLATE, authenticated=False, hostname=socket.gethostname(), tx_msg=tx_msg, onboard_msg=onboard_msg)

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("login_name")
    pin = request.form.get("login_pin")
    
    try:
        # Query backend ledger endpoint securely passing name and PIN credentials
        resp = requests.post(f"{LEDGER_URL}/ledger/login", json={"name": name, "pin": pin}, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return render_template_string(HTML_TEMPLATE,
                                        authenticated=True,
                                        account_id=data["account_id"],
                                        account_holder=data["account_holder"],
                                        balance=data["balance"],
                                        hostname=socket.gethostname(),
                                        tx_msg="Access Authorized. Secure Session Established.")
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        
    return redirect(url_for("index", tx_msg="ACCESS DENIED: Authentication credentials failed matching criteria."))

@app.route("/transfer", methods=["POST"])
def transfer():
    source = request.form.get("source_account")
    name = request.form.get("authenticated_name")
    dest = request.form.get("destination_account")
    amount_raw = request.form.get("amount")
    balance_raw = request.form.get("authenticated_balance")
    
    try:
        # Clean up any potential formatting symbols or trailing spaces
        clean_bal = float(str(balance_raw).replace('$', '').replace(',', '').strip())
        amount = float(str(amount_raw).strip())
        
        # Verify if the user actually has enough money before calling the switch
        if amount > clean_bal:
            return render_template_string(HTML_TEMPLATE, authenticated=True, account_id=source, account_holder=name, balance=clean_bal, hostname=socket.gethostname(), tx_msg="DECLINED: Insufficient vault funds for wire transfer.")
            
        payload = {"account_id": source, "destination_account": dest, "amount": amount}
        resp = requests.post(SWITCH_URL, json=payload, timeout=5)
        
        if resp.status_code == 200:
            new_balance = clean_bal - amount
            return render_template_string(HTML_TEMPLATE, 
                                        authenticated=True, 
                                        account_id=source, 
                                        account_holder=name, 
                                        balance=new_balance, 
                                        hostname=socket.gethostname(), 
                                        tx_msg=f"TRANSACTION APPROVED: ${amount:.2f} successfully wired to Account {dest}.")
        else:
            reason = resp.json().get('reason', 'Processing rejection')
            return render_template_string(HTML_TEMPLATE, authenticated=True, account_id=source, account_holder=name, balance=clean_bal, hostname=socket.gethostname(), tx_msg=f"DECLINED: {reason}")
            
    except Exception as e:
        logging.error(f"Transfer routing link failed to execute: {str(e)}")
        # Safe fallback: preserve the original balance if the calculation or parsing catches an anomaly
        try:
            fallback_bal = float(str(balance_raw).replace('$', '').replace(',', '').strip())
        except:
            fallback_bal = 0.0
            
    return render_template_string(HTML_TEMPLATE, authenticated=True, account_id=source, account_holder=name, balance=fallback_bal, hostname=socket.gethostname(), tx_msg="GATEWAY ERROR: Transaction processing system link timeout.")

@app.route("/onboard", methods=["POST"])
def onboard():
    name = request.form.get("customer_name")
    deposit = request.form.get("initial_deposit")
    pin = request.form.get("customer_pin")
    
    try:
        payload = {"name": name, "initial_deposit": deposit, "pin": pin}
        resp = requests.post(ONBOARDING_URL, json=payload, timeout=5)
        if resp.status_code == 201:
            data = resp.json()
            msg = f"SUCCESS! Vault profile created for {data['account_holder']}. You can login now."
            return redirect(url_for("index", onboard_msg=msg))
    except Exception as e:
        logging.error(f"Onboarding error: {str(e)}")
        
    return redirect(url_for("index", tx_msg="Registration failed to write configuration parameters."))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)