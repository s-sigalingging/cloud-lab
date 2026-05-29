from flask import Flask, request, jsonify
import psycopg2
import os
import logging
from urllib.parse import unquote_plus

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DB_NAME = os.getenv("DB_NAME", "ledger_db")
DB_USER = os.getenv("DB_USER", "ledger_admin")

# DYNAMIC LOOKUP: Read the bundled JSON secret file mounted by GKE
def load_database_credentials():
    secret_path = "/var/secrets/db_credentials.json"
    
    # Default fallbacks for safe local development / docker testing
    credentials = {
        "DB_HOST": "127.0.0.1",
        "DB_PASS": "local_development_password"
    }
    
    if os.path.exists(secret_path):
        try:
            with open(secret_path, "r") as f:
                credentials = json.load(f)
                logging.info("Successfully loaded database credentials from GSM CSI volume.")
        except Exception as e:
            logging.error(f"Failed to read or parse GSM CSI secret volume file: {str(e)}")
            
    return credentials

# Clean connection wrapper using our dynamic secret manager values
def get_db_connection():
    creds = load_database_credentials()
    return psycopg2.connect(
        host=creds.get("DB_HOST"),
        database=DB_NAME,
        user=DB_USER,
        password=creds.get("DB_PASS")
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Added pin column to the database schema
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id VARCHAR(50) PRIMARY KEY,
                account_holder VARCHAR(100) NOT NULL,
                balance NUMERIC(15, 2) NOT NULL CHECK (balance >= 0),
                pin VARCHAR(10) NOT NULL DEFAULT '1234'
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        logging.info("[LEDGER DATABASE] Schema verified with secure PIN support.")
    except Exception as e:
        logging.error(f"[DATABASE INIT ERROR]: {str(e)}")

init_db()

@app.route("/healthz", methods=["GET"])
def health_check():
    return {"status": "HEALTHY"}, 200

# NEW SECURE LOGIN ENDPOINT
@app.route("/ledger/login", methods=["POST"])
def verify_login():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        user_pin = data.get("pin", "").strip()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify both name and PIN match perfectly
        cur.execute("SELECT account_id, account_holder, balance FROM accounts WHERE LOWER(account_holder) = LOWER(%s) AND pin = %s;", (name, user_pin))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if row:
            return {
                "status": "AUTHENTICATED",
                "account_id": row[0],
                "account_holder": row[1],
                "balance": float(row[2])
            }, 200
        else:
            return {"status": "DENIED", "reason": "Invalid legal name or secure PIN credentials."}, 401
            
    except Exception as e:
        logging.error(f"[LOGIN AUTH ERROR] {str(e)}")
        return {"status": "ERROR", "reason": "Database authentication link failure"}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)