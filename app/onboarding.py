from flask import Flask, request, jsonify
import psycopg2
import os
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Pull the private Cloud SQL IP address from Kubernetes Environment variables
DB_HOST = os.getenv("DB_HOST", "YOUR_DB_INTERNAL_IP")
DB_NAME = "ledger_db"
DB_USER = "ledger_admin"
DB_PASS = "SuperSecureBankingPassword2026!"

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route("/healthz", methods=["GET"])
def health_check():
    return {"status": "HEALTHY"}, 200

@app.route("/api/v1/onboard", methods=["POST"])
def onboard_user():
    data = request.get_json()
    if not data or "name" not in data or "initial_deposit" not in data:
        return jsonify({"status": "REJECTED", "error": "Missing onboarding information"}), 400
        
    name = data["name"]
    initial_deposit = float(data["initial_deposit"])
    
    # Generate a unique mock account number starting with '111'
    account_id = f"111{random.randint(1000, 9999)}"
    
    logging.info(f"[ONBOARDING] Initiating new account creation for {name} with initial deposit: ${initial_deposit}")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Write the new client profile straight to Cloud SQL disk storage
        cur.execute(
            "INSERT INTO accounts (account_id, account_holder, balance) VALUES (%s, %s, %s);",
            (account_id, name, initial_deposit)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        logging.info(f"[ONBOARDING SUCCESS] Account {account_id} permanently saved to database.")
        return jsonify({
            "status": "SUCCESS",
            "account_id": account_id,
            "account_holder": name,
            "balance": initial_deposit
        }), 201
        
    except Exception as e:
        logging.error(f"[ONBOARDING CRITICAL ERROR] Database commit failed: {str(e)}")
        return jsonify({"status": "ERROR", "reason": "Database allocation failure"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)