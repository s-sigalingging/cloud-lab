from flask import Flask, request, jsonify
import psycopg2
import os
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Direct Cloud SQL Private Network Parameters
DB_HOST = "10.189.0.3"
DB_NAME = "ledger_db"
DB_USER = "ledger_admin"
DB_PASS = "SuperSecureBankingPassword2026!"

# Internal GKE URL for the Core Ledger Service
LEDGER_URL = os.getenv("LEDGER_SERVICE_URL", "http://core-ledger-service.app.svc.cluster.local:8082")

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route("/healthz", methods=["GET"])
def health_check():
    return {"status": "HEALTHY"}, 200

@app.route("/api/v1/switch/process", methods=["POST"])
def process_transit():
    data = request.get_json()
    if not data or "account_id" not in data or "destination_account" not in data or "amount" not in data:
        return jsonify({"status": "DECLINED", "reason": "Malformed transit request payload"}), 400
        
    source = data["account_id"]
    destination = data["destination_account"]
    
    try:
        amount = float(data["amount"])
    except ValueError:
        return jsonify({"status": "DECLINED", "reason": "Invalid transaction amount format"}), 400

    logging.info(f"[PAYMENT SWITCH] Processing transit authorization request for account {source} to {destination}: ${amount}")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Compliance Check: Ensure the destination account exists in our registry
        cur.execute("SELECT account_id, balance FROM accounts WHERE account_id = %s;", (destination,))
        dest_account = cur.fetchone()
        
        if not dest_account:
            cur.close()
            conn.close()
            logging.warning(f"[PAYMENT SWITCH REJECTION] Destination account {destination} not found.")
            return jsonify({"status": "DECLINED", "reason": "Ledger rejection on compliance verification"}), 400

        # 2. Balance Check: Verify the source account has enough funds available
        cur.execute("SELECT balance FROM accounts WHERE account_id = %s;", (source,))
        source_account = cur.fetchone()
        
        if not source_account or float(source_account[0]) < amount:
            cur.close()
            conn.close()
            logging.warning(f"[PAYMENT SWITCH REJECTION] Insufficient funds or source account missing: {source}")
            return jsonify({"status": "DECLINED", "reason": "Insufficient balance to clear transit execution"}), 400

        # 3. Transaction Execution: Deduct from source, add to destination
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s;", (amount, source))
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s;", (amount, destination))
        
        conn.commit()
        cur.close()
        conn.close()

        logging.info(f"[PAYMENT SWITCH SUCCESS] Transaction complete: ${amount} from {source} to {destination}")
        return jsonify({"status": "APPROVED", "message": "Transaction cleared payment switch routing matrix."}), 200

    except Exception as e:
        logging.error(f"[PAYMENT SWITCH CRITICAL ERROR] Execution failed: {str(e)}")
        return jsonify({"status": "ERROR", "reason": "Internal transaction processing failure"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)