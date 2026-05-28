from flask import Flask, request, jsonify
import psycopg2
import os
import logging
from urllib.parse import unquote_plus  # Robust variant decoder

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Direct Cloud SQL Private Network Parameters
DB_HOST = "10.189.0.3"
DB_NAME = "ledger_db"
DB_USER = "ledger_admin"
DB_PASS = "SuperSecureBankingPassword2026!"

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route("/healthz", methods=["GET"])
def health_check():
    return {"status": "HEALTHY"}, 200

@app.route("/ledger/balance/<lookup_value>", methods=["GET"])
def get_balance(lookup_value):
    try:
        # Normalize incoming variable data (e.g., handles both 'Bassura%20City' and 'Bassura+City' completely)
        decoded_name = unquote_plus(lookup_value).strip()
        
        logging.info(f"[LEDGER ENGINE] Querying database record state for: '{decoded_name}'")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # S-Shield Smart Lookup Strategy
        if decoded_name.startswith("111") or decoded_name.startswith("ACC"):
            cur.execute("SELECT account_id, account_holder, balance FROM accounts WHERE account_id = %s;", (decoded_name,))
        else:
            cur.execute("SELECT account_id, account_holder, balance FROM accounts WHERE LOWER(account_holder) = LOWER(%s);", (decoded_name,))
            
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return {
                "status": "FOUND",
                "account_id": row[0],
                "account_holder": row[1],
                "balance": float(row[2])
            }, 200
        else:
            logging.warning(f"[LEDGER ENGINE] No registry entries match lookups for: '{decoded_name}'")
            return {"status": "NOT_FOUND", "reason": "No banking records match that registration profile"}, 404
            
    except Exception as e:
        logging.error(f"[LEDGER ENGINE CRITICAL FAILURE] Execution trace crashed: {str(e)}")
        return {"status": "ERROR", "reason": "Internal storage connection failure"}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)