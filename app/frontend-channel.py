@app.route("/ledger/balance/<lookup_value>", methods=["GET"])
def get_balance(lookup_value):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # S-Shield Smart Lookup: Check if it's an ID (starts with 111/ACC) or a full legal name
        if lookup_value.startswith("111") or lookup_value.startswith("ACC"):
            cur.execute("SELECT account_id, account_holder, balance FROM accounts WHERE account_id = %s;", (lookup_value,))
        else:
            # Drop trailing spaces and do a case-insensitive query to find the legal name match
            cur.execute("SELECT account_id, account_holder, balance FROM accounts WHERE LOWER(account_holder) = LOWER(%s);", (lookup_value.strip(),))
            
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
            return {"status": "NOT_FOUND", "reason": "No banking records match that registration profile"}, 404
            
    except Exception as e:
        logging.error(f"[LEDGER ENGINE ERROR] Lookup execution crashed: {str(e)}")
        return {"status": "ERROR", "reason": "Internal storage connection failure"}, 500