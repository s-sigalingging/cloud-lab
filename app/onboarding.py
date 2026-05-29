from flask import Flask, request, jsonify
import psycopg2
import os
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Verified Cloud SQL Private Network Parameters
DB_HOST = "10.189.0.3"
DB_NAME = "ledger_db"
DB_USER = "ledger_admin"
DB_PASS = "SuperSecureBankingPassword2026!"

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route("/healthz", methods=["GET"])
def health_check():
    # Simple connection check to ensure the service boots cleanly
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "HEALTHY"}, 200
    except Exception as e:
        logging.error(f"Health check database connection failure: {str(e)}")
        return {"status": "UNHEALTHY", "reason": "Database connection failed"}, 500

@app.route("/api/v1/onboard", methods=["POST"])
def onboard_user():
    data = request.get_json()
    if not data or "name" not in data or "initial_deposit" not in data or "pin" not in data:
        return jsonify({"status": "REJECTED", "error": "Missing onboarding information or PIN specification"}), 400
        
    name = data["name"]
    initial_deposit = float(data["initial_deposit"])
    pin = str(data["pin"]).strip()
    
    # Generate a fresh 7-digit Account ID
    account_id = f"111{random.randint(1000, 9999)}"
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Correctly insert rows into the updated schema with the pin column included
        cur.execute(
            "INSERT INTO accounts (account_id, account_holder, balance, pin) VALUES (%s, %s, %s, %s);",
            (account_id, name, initial_deposit, pin)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        logging.info(f"[ONBOARDING SUCCESS] Created account {account_id} for {name}")
        return jsonify({
            "status": "SUCCESS",
            "account_id": account_id,
            "account_holder": name
        }), 201
        
    except Exception as e:
        logging.error(f"Onboarding database transaction failed: {str(e)}")
        return jsonify({"status": "ERROR", "reason": "Internal ledger write failure"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)