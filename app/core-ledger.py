from flask import Flask, request, jsonify
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# In-memory mock database state for S-Shield accounts
MOCK_DATABASE = {
    "ACC-771B0355": 5240.50,
    "ACC-992A1144": 12500.00
}

@app.route("/ledger/mutate", methods=["POST"])
def mutate_balance():
    data = request.get_json()
    
    account_id = data.get("account_id")
    amount = float(data.get("amount", 0))
    action = data.get("action") # CREDIT or DEBIT

    if account_id not in MOCK_DATABASE:
        logging.error(f"[LEDGER ERROR] Rejection: Account {account_id} not found.")
        return jsonify({"status": "REJECTED", "reason": "Invalid account metadata"}), 404

    logging.info(f"[LEDGER] Processing data mutation payload. Account: {account_id} | Action: {action} | Impact: ${amount}")

    # Process financial arithmetic safely
    if action == "DEBIT":
        if MOCK_DATABASE[account_id] < abs(amount):
            return jsonify({"status": "REJECTED", "reason": "Insufficient ledger collateral"}), 400
        MOCK_DATABASE[account_id] -= abs(amount)
    elif action == "CREDIT":
        MOCK_DATABASE[account_id] += abs(amount)

    # Generate a cryptographically structured mock transaction ID
    generated_tx_id = f"TXN-{random.randint(100000, 999999)}"
    logging.info(f"[LEDGER UPDATE] New Balance for {account_id}: ${MOCK_DATABASE[account_id]:.2f}")

    return jsonify({
        "tx_id": generated_tx_id,
        "status": "COMMITTED",
        "new_balance": MOCK_DATABASE[account_id]
    }), 200

# Endpoint for frontend UI to fetch the raw data safely via internal query
@app.route("/ledger/balance/<account_id>", methods=["GET"])
def get_balance(account_id):
    if account_id in MOCK_DATABASE:
        return jsonify({"account_id": account_id, "balance": MOCK_DATABASE[account_id]}), 200
    return jsonify({"error": "Account not found"}), 404

if __name__ == "__main__":
    # Internal cluster backend port
    app.run(host="0.0.0.0", port=8082)