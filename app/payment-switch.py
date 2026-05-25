from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Dynamic environment routing targets (Aligned to our core-ledger service port 8082)
LEDGER_URL = os.getenv("LEDGER_SERVICE_URL", "http://core-ledger-service.app.svc.cluster.local:8082/ledger/mutate")

@app.route("/api/v1/switch/process", methods=["POST"])
def process_transaction():
    data = request.get_json()
    
    # 1. Structural Sanity Verification
    if not data or "account_id" not in data or "amount" not in data:
        return jsonify({"status": "REJECTED", "error": "Malformed transaction payload"}), 400
        
    account_id = data["account_id"]
    amount = float(data["amount"])
    
    logging.info(f"[PAYMENT SWITCH] Processing transit authorization request for account {account_id}: ${amount}")
    
    # 2. Fraud & Compliance Safeguards (Velocity Checks)
    if amount > 10000.00:
        logging.warning(f"[SECURITY ALERT] Transaction flagged: ${amount} exceeds automated compliance limits.")
        return jsonify({"status": "DECLINED", "reason": "Exceeds automated single-transit threshold"}), 403

    # 3. Secure Handshake with Core Ledger
    try:
        # CORRECTION: Hardcoded to "DEBIT" so outgoing money authorizations deduct funds from the ledger database pool
        ledger_payload = {
            "account_id": account_id, 
            "amount": amount, 
            "action": "DEBIT"
        }
        
        response = requests.post(LEDGER_URL, json=ledger_payload, timeout=5)
        
        if response.status_code == 200:
            logging.info(f"[PAYMENT SWITCH] Ledger reconciliation successful for {account_id}")
            return jsonify({"transaction_id": response.json().get("tx_id"), "status": "APPROVED"})
        else:
            return jsonify({"status": "FAILED", "reason": "Ledger rejection on compliance verification"}), 500
            
    except requests.exceptions.RequestException as e:
        logging.error(f"[CRITICAL] Lost connectivity to Core Ledger: {str(e)}")
        return jsonify({"status": "ERROR", "reason": "Core Ledger gateway timeout"}), 504

if __name__ == "__main__":
    # Internal cluster service port
    app.run(host="0.0.0.0", port=8081)