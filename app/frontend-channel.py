from flask import Flask, render_template_string, request, redirect, url_for
import requests
import os
import logging
import socket

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Internal GKE Cluster Routing URLs
LEDGER_URL = os.getenv("LEDGER_SERVICE_URL", "http://core-ledger-service.app.svc.cluster.local:8082")
SWITCH_URL = os.getenv("SWITCH_SERVICE_URL", "http://payment-switch-service.app.svc.cluster.local:8081/api/v1/switch/process")
ONBOARDING_URL = os.getenv("ONBOARDING_SERVICE_URL", "http://onboarding.app.svc.cluster.local:8083/api/v1/onboard")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>S-Shield Neobank Core Portal</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; display: flex; gap: 20px; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); flex: 1; }
        h2 { color: #0A58CA; margin-top: 0; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
        .balance { font-size: 36px; color: #212529; font-weight: bold; margin: 15px 0; font-family: monospace; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; font-size: 11px; color: #6c757d; margin-bottom: 5px; font-weight: bold; letter-spacing: 0.5px; }
        .input-group input { width: 100%; padding: 12px; border: 1px solid #ced4da; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { background-color: #0D6EFD; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; transition: background 0.2s; }
        .btn:hover { background-color: #0b5ed7; }
        .btn-success { background-color: #198754; }
        .btn-success:hover { background-color: #157347; }
        .alert { padding: 12px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; font-weight: bold; }
        .alert-success { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }
        .alert-danger { background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }
        .footer { text-align: center; color: #6c757d; font-size: 11px; margin-top: 30px; font-family: monospace; }
    </style>
</head>
<body>
    <div style="text-align:center; margin-bottom: 30px;">
        <h1 style="color: #212529; margin-bottom: 5px;">🛡️ S-Shield Neobank</h1>
        <p style="color: #6c757d; margin-top: 0;">GKE Multi-Tier Production Ledger Portal</p>
    </div>

    <div class="container">
        <div class="card">
            <h2>Account Vault View</h2>
            {% if tx_msg %}
                <div class="alert {% if 'APPROVED' in tx_msg or 'Active' in tx_msg or 'SUCCESS' in tx_msg %}alert-success{% else %}alert-danger{% endif %}">{{ tx_msg }}</div>
            {% endif %}
            
            <form action="/" method="GET" style="display: flex; gap: 10px; margin-bottom: 20px;">
                <input type="text" name="lookup_name" placeholder="Enter Full Legal Name to load..." value="{{ search_query }}" style="flex: 1; padding: 10px; border: 1px solid #ced4da; border-radius: 6px;" required>
                <button type="submit" class="btn" style="width: auto; padding: 0 20px;">Load Account</button>
            </form>

            <p style="color: #6c757d; margin-bottom: 2px; font-size: 11px; font-weight: bold;">ACCOUNT HOLDER</p>
            <h3 style="margin-top: 0; color: #495057;">{{ account_holder }}</h3>

            <p style="color: #6c757d; margin-bottom: 2px; font-size: 11px; font-weight: bold;">ASSIGNED ACCOUNT ID</p>
            <h4 style="margin-top: 0; font-family: monospace; color: #0A58CA;">{{ account_id or "--------" }}</h4>
            
            <p style="color: #6c757d; margin-bottom: 2px; font-size: 11px; font-weight: bold;">CURRENT BALANCE</p>
            <div class="balance">${{ "%.2f"|format(balance) }}</div>
            
            <form action="/transfer" method="POST" style="margin-top: 25px;">
                <input type="hidden" name="source_account" value="{{ account_id }}">
                <input type="hidden" name="search_query" value="{{ search_query }}">
                <div class="input-group">
                    <label>DESTINATION ACCOUNT ID</label>
                    <input type="text" name="destination_account" placeholder="e.g., 111002" required>
                </div>
                <div class="input-group">
                    <label>TRANSFER AMOUNT ($)</label>
                    <input type="number" step="0.01" name="amount" placeholder="0.00" required>
                </div>
                <button type="submit" class="btn">Send Authorization</button>
            </form>
        </div>

        <div class="card" style="border-top: 4px solid #198754;">
            <h2>Customer Onboarding</h2>
            {% if onboard_msg %}
                <div class="alert alert-success">{{ onboard_msg }}</div>
            {% endif %}
            <p style="color: #6c757d; font-size: 13px; margin-bottom: 20px;">Instantly register a new bank account row directly into our secure Private Cloud SQL PostgreSQL database instance.</p>
            
            <form action="/onboard" method="POST">
                <div class="input-group">
                    <label>FULL LEGAL NAME</label>
                    <input type="text" name="customer_name" placeholder="e.g., Silverius Sigalingging" required>
                </div>
                <div class="input-group">
                    <label>INITIAL OPENING DEPOSIT ($)</label>
                    <input type="number" step="0.01" name="initial_deposit" placeholder="500.00" required>
                </div>
                <button type="submit" class="btn btn-success">Open New Account</button>
            </form>
        </div>
    </div>

    <div class="footer">
        Frontend Runtime Node: {{ hostname }} | Database Engine: Cloud SQL Private Peering
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    search_query = request.args.get("lookup_name", "").strip()
    tx_msg = request.args.get("tx_msg")
    onboard_msg = request.args.get("onboard_msg")
    
    if not search_query:
        return render_template_string(HTML_TEMPLATE, 
                                    search_query="",
                                    account_id="",
                                    account_holder="Please enter your name to pull your secure profile",
                                    balance=0.0,
                                    hostname=socket.gethostname(),
                                    tx_msg=tx_msg or "System Status: Online & Secure",
                                    onboard_msg=onboard_msg)
    
    try:
        resp = requests.get(f"{LEDGER_URL}/ledger/balance/{search_query}", timeout=3)
        if resp.status_code == 200:
            ledger_data = resp.json()
            return render_template_string(HTML_TEMPLATE, 
                                        search_query=search_query,
                                        account_id=ledger_data["account_id"],
                                        account_holder=ledger_data["account_holder"],
                                        balance=ledger_data["balance"],
                                        hostname=socket.gethostname(),
                                        tx_msg=tx_msg or "Connection Status: Active Secure Link",
                                        onboard_msg=onboard_msg)
        else:
            tx_msg = "ERROR: Registration record details not found for that name."
    except Exception as e:
        logging.error(f"Ledger connectivity error: {str(e)}")
        tx_msg = "ERROR: Could not reach central ledger database node"
        
    return render_template_string(HTML_TEMPLATE, 
                                  search_query=search_query, 
                                  account_id="", 
                                  account_holder="Profile Not Found", 
                                  balance=0.0, 
                                  hostname=socket.gethostname(), 
                                  tx_msg=tx_msg, 
                                  onboard_msg=onboard_msg)

@app.route("/transfer", methods=["POST"])
def transfer():
    source = request.form.get("source_account")
    search_query = request.form.get("search_query")
    dest = request.form.get("destination_account")
    amount = request.form.get("amount")
    
    try:
        payload = {"account_id": source, "destination_account": dest, "amount": amount}
        resp = requests.post(SWITCH_URL, json=payload, timeout=5)
        msg = f"TRANSACTION APPROVED: Routed via Payment Switch." if resp.status_code == 200 else f"DECLINED: {resp.json().get('reason', 'Processing error')}"
    except Exception as e:
        msg = f"GATEWAY ERROR: {str(e)}"
        
    return redirect(url_for("index", lookup_name=search_query, tx_msg=msg))

@app.route("/onboard", methods=["POST"])
def onboard():
    name = request.form.get("customer_name")
    deposit = request.form.get("initial_deposit")
    
    try:
        payload = {"name": name, "initial_deposit": deposit}
        resp = requests.post(ONBOARDING_URL, json=payload, timeout=5)
        if resp.status_code == 201:
            data = resp.json()
            msg = f"SUCCESS! Account {data['account_id']} created for {data['account_holder']}."
            return redirect(f"/?lookup_name={data['account_holder']}&onboard_msg={msg}")
            
    except Exception as e:
        logging.error(f"Onboarding endpoint error: {str(e)}")
        
    return redirect(url_for("index", tx_msg="Onboarding service failed to commit user."))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)