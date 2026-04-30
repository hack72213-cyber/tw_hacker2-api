from flask import Flask, request, jsonify
import requests
import secrets
from datetime import datetime, timedelta
import os

app = Flask(__name__)

ADMIN_KEY = "TW_ADMIN_159357"
KEYS_DB = {}

def generate_key(customer, days):
    key_id = secrets.token_hex(8).upper()
    api_key = f"TW_{key_id}"
    expires = datetime.now() + timedelta(days=int(days))
    KEYS_DB[api_key] = {"customer": customer, "expires": expires.isoformat(), "status": "active", "created": datetime.now().isoformat()}
    return api_key

def check_key(api_key):
    if api_key not in KEYS_DB: return None
    key_data = KEYS_DB[api_key]
    if key_data["status"] != "active": return "revoked"
    if datetime.now() > datetime.fromisoformat(key_data["expires"]): 
        key_data["status"] = "expired"
        return "expired"
    return key_data

@app.route('/')
def home():
    return jsonify({
        "service": "🔥 TW HACKER2 API 🔥",
        "owner": "@tw_hacker2",
        "status": "🟢 Live 24/7",
        "endpoints": {
            "GET /api/user": "?api_key=KEY&term=TG_ID",
            "GET /api/mobile": "?api_key=KEY&term=NUMBER",
            "GET /admin/gen": "?admin_key=TW_ADMIN_159357&customer=@name&days=7"
        },
        "how_to_buy": "DM @tw_hacker2 on Telegram"
    })

@app.route('/api/user')
def get_user():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required. Buy from @tw_hacker2"}), 401
    
    result = check_key(api_key)
    if not result:
        return jsonify({"error": "Invalid API key"}), 401
    if result == "expired":
        return jsonify({"error": "Key expired. Renew at @tw_hacker2"}), 401
    if result == "revoked":
        return jsonify({"error": "Key revoked"}), 401
    
    term = request.args.get('term')
    if not term:
        return jsonify({"error": "term required (Telegram ID)"}), 400
    
    # Call original API with key rotation
    original = "https://users-xinfo-admin.vercel.app/api"
    backup_keys = ["demo", "test", "free", "trial", "guest", "dev"]
    
    for key in backup_keys:
        try:
            r = requests.get(f"{original}?key={key}&type=user&term={term}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                data["developer"] = "@tw_hacker2"
                data["api_key_owner"] = result["customer"]
                data["bypassed_by"] = "OGGY_BHAI"
                return jsonify(data)
        except:
            continue
    
    return jsonify({"error": "Lookup failed"}), 500

@app.route('/api/mobile')
def get_mobile():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required"}), 401
    
    result = check_key(api_key)
    if not result or result in ["expired", "revoked"]:
        return jsonify({"error": f"Key {result}" if result != "revoked" else "Key revoked"}), 401
    
    term = request.args.get('term')
    if not term:
        return jsonify({"error": "term required (Mobile number)"}), 400
    
    original = "https://users-xinfo-admin.vercel.app/api"
    backup_keys = ["demo", "test", "free", "trial", "guest", "dev"]
    
    for key in backup_keys:
        try:
            r = requests.get(f"{original}?key={key}&type=mobile&term={term}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                data["developer"] = "@tw_hacker2"
                data["api_key_owner"] = result["customer"]
                return jsonify(data)
        except:
            continue
    
    return jsonify({"error": "Lookup failed"}), 500

@app.route('/admin/gen')
def admin_gen():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized. Contact @tw_hacker2"}), 401
    
    customer = request.args.get('customer')
    days = request.args.get('days', '7')
    
    if not customer:
        return jsonify({"error": "customer parameter required"}), 400
    
    try:
        days = int(days)
        if days not in [1, 7, 30]:
            days = 7
    except:
        days = 7
    
    api_key = generate_key(customer, days)
    
    # Price calculation
    prices = {1: "₹100", 7: "₹500", 30: "₹1500"}
    
    return jsonify({
        "success": True,
        "api_key": api_key,
        "customer": customer,
        "valid_days": days,
        "price": prices.get(days, "₹500"),
        "expires": KEYS_DB[api_key]["expires"],
        "endpoints": {
            "user_lookup": f"/api/user?api_key={api_key}&term=TG_ID",
            "mobile_lookup": f"/api/mobile?api_key={api_key}&term=NUMBER"
        }
    })

@app.route('/admin/check')
def admin_check():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required"}), 400
    
    result = check_key(api_key)
    if not result:
        return jsonify({"valid": False, "error": "Key not found"})
    if result in ["expired", "revoked"]:
        return jsonify({"valid": False, "error": f"Key is {result}"})
    
    return jsonify({
        "valid": True,
        "customer": result["customer"],
        "expires": result["expires"],
        "created": result["created"],
        "status": result["status"]
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found. Visit / for documentation"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("🔥 TW HACKER2 API STARTED 🔥")
    print(f"📍 Running on port {port}")
    print(f"👤 Owner: @tw_hacker2")
    app.run(host='0.0.0.0', port=port)
