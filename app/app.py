from flask import Flask, render_code, request, jsonify
import os
import socket

app = Flask(__name__)

# Basic landing page displaying bank branding and pod data
@app.route('/', methods=['GET'])
def index():
    pod_name = socket.gethostname()
    return f"""
    <html>
        <head>
            <title>Secure GCP Mobile Banking</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f6f9; }}
                .card {{ background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; }}
                h1 {{ color: #0A58CA; }}
                .balance {{ font-size: 24px; color: #198754; font-weight: bold; margin: 20px 0; }}
                .footer {{ color: #6c757d; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>S-Shield Neobank</h1>
                <p><strong>Account Holder:</strong> Silver Sigalingging</p>
                <div class="balance">Wallet Balance: $5,240.50</div>
                <p>Status: <span style="color: green; font-weight: bold;">CONNECTED TO SECURE VPC</span></p>
                <div class="footer">Served by Cluster Node Host: {pod_name}</div>
            </div>
        </body>
    </html>
    """

# API Endpoint simulating our Switching Middleware router
@app.route('/api/v1/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    
    if not data or 'destination_account' not in data or 'amount' not in data:
        return jsonify({"status": "ERROR", "message": "Invalid transaction payload"}), 400
        
    dest = str(data['destination_account'])
    amount = data['amount']
    
    # Simulating switching middleware logic based on card/account bin prefixes
    if dest.startswith('111'):
        routing_path = "INTERNAL_CORE_LEDGER"
        message = f"Successfully routed ${amount} internally to account {dest}."
    elif dest.startswith('999'):
        routing_path = "EXTERNAL_PAYMENT_SWITCH"
        message = f"Routed ${amount} via interbank clearing network to external bank."
    else:
        routing_path = "DEFAULT_ROUTER"
        message = f"Processing standard routing matrix for destination {dest}."

    return jsonify({
        "status": "PROCESSED",
        "switching_route": routing_path,
        "amount": amount,
        "destination": dest,
        "gateway_message": message
    }), 200

if __name__ == '__main__':
    # Listen on port 8080 (standard for container environments)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)