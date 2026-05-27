from flask import Flask, request, jsonify
import psycopg2
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv("DB_HOST", "YOUR_DB_INTERNAL_IP")
DB_NAME = "ledger_db"
DB_USER = "ledger_admin"
DB_PASS = "SuperSecureBankingPassword2026!"

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

# Bootstrapping function: Builds our database tables automatically if they don't exist yet
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id VARCHAR(50) PRIMARY KEY,
                account_holder VARCHAR(100) NOT NULL,
                balance NUMERIC(15, 2) NOT NULL CHECK (balance >= 0)
            );
        """)
        # Seed default lab record for Silver if table is fresh
        cur.execute("""
            INSERT INTO accounts (account_id, account_holder, balance)
            VALUES ('ACC-771B0355', 'Silver Sigalingging', 5240.50)
            ON CONFLICT (account_id) DO NOTHING;
        """)
        conn.commit()
        cur.close()
        conn.close()
        logging.info("[LEDGER DATABASE] Tables verified and initialized successfully.")
    except Exception as e:
        logging.error(f"[DATABASE INIT FAILURE] Could not initialize tables: {str(e)}")

@app.route("/ledger/balance/<account_id>", methods=["GET"])
def get_balance(account_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT account_holder, balance FROM accounts WHERE account_id = %s;", (account_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return jsonify({"account_id": account_id, "account_holder": result[0], "balance": float(result[1])}), 200
        return jsonify({"status": "NOT_FOUND", "error": "Account does not exist"}), 404
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@app.route("/ledger/mutate", methods=["POST"])
def mutate_balance():
    data = request.get_json()
    account_id = data.get("account_id", "ACC-771B0355")
    amount = float(data.get("amount", 0))
    action = data.get("action", "DEBIT")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if action == "DEBIT":
            # Deduct funds securely from the sender row
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s;", (amount, account_id))
            
        conn.commit()
        cur.close()
        conn.close()
        logging.info(f"[LEDGER COMMIT] Successfully debited ${amount} from account {account_id}")
        return jsonify({"status": "COMMITTED", "tx_id": "TX-SQL-SUCCESS"}), 200
    except Exception as e:
        logging.error(f"[LEDGER REJECTION] Transaction rolled back: {str(e)}")
        return jsonify({"status": "REJECTED", "reason": "Insufficient funds or account error"}), 400

if __name__ == "__main__":
    init_db() # Run automatic table generation on boot
    app.run(host="0.0.0.0", port=8082)