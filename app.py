from flask import Flask, request, jsonify
import requests
import secrets
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# CONFIG - APNI VALUES YAHAN CHANGE KAR
ADMIN_KEY = "ADMIN_TW_159357"  # Ye tu admin commands ke liye use karega
PRICES = {"1day": "₹100", "7days": "₹500", "1month": "₹1500"}

# Database (file based - Render restart pe bhi rahega thoda time)
KEYS_DB = {}

def generate_key(customer, days):
    key_id = secrets.token_hex(8).upper()
    api_key = f"TW_{key_id}"
    expires = datetime.now() + timedelta(days=int(days))
    KEYS_DB[api_key] = {
        "customer": customer,
        "expires": expires.isoformat(),
        "created": datetime.now().isoformat(),
        "status": "active"
    }
    return api_key, expires

def check_key(api_key):
    if api_key not in KEYS_DB:
        return None
    key_data = KEYS_DB[api_key]
    if key_data["status"] != "active":
        return "revoked"
    if datetime.now() > datetime.fromisoformat(key_data["expires"]):
        return "expired"
    return key_data

@app.route('/')
def home():
    return jsonify({
        "service": "🔥 TW HACKER2 API 🔥",
        "owner": "@tw_hacker2",
        "status": "🟢 Online 24/7",
        "endpoints": {
            "GET /api/user": "?api_key=KEY&term=TG_ID",
            "GET /api/mobile": "?api_key=KEY&term=NUMBER",
            "GET /admin/gen": "?admin_key=ADMIN_KEY&customer=@name&days=7",
            "GET /admin/list": "?admin_key=ADMIN_KEY",
            "GET /admin/revoke": "?admin_key=ADMIN_KEY&api_key=TW_XXX"
        },
        "pricing": PRICES,
        "buy": "DM @tw_hacker2"
    })

@app.route('/api/user')
def get_user():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required", "buy": "DM @tw_hacker2"}), 401
    
    result = check_key(api_key)
    if not result:
        return jsonify({"error": "Invalid API key"}), 401
    if result == "expired":
        return jsonify({"error": "Key expired. Renew: DM @tw_hacker2"}), 401
    if result == "revoked":
        return jsonify({"error": "Key revoked"}), 401
    
    term = request.args.get('term')
    if not term:
        return jsonify({"error": "term required (Telegram ID)"}), 400
    
    # Call original API (unlimited bypass)
    original = "https://users-xinfo-admin.vercel.app/api"
    for key in ["demo", "test", "free", "trial", "guest"]:
        try:
            r = requests.get(f"{original}?key={key}&type=user&term={term}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                data["developer"] = "@tw_hacker2"
                data["api_key_owner"] = result["customer"]
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
        return jsonify({"error": f"Key {result}" if result else "Invalid key"}), 401
    
    term = request.args.get('term')
    if not term:
        return jsonify({"error": "term required (Mobile number)"}), 400
    
    original = "https://users-xinfo-admin.vercel.app/api"
    for key in ["demo", "test", "free", "trial", "guest"]:
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
        return jsonify({"error": "Unauthorized"}), 401
    
    customer = request.args.get('customer')
    days = request.args.get('days', '7')
    
    if not customer:
        return jsonify({"error": "customer required"}), 400
    
    api_key, expires = generate_key(customer, days)
    return jsonify({
        "success": True,
        "api_key": api_key,
        "customer": customer,
        "expires": expires.isoformat(),
        "price": PRICES.get(f"{days}days", PRICES["7days"])
    })

@app.route('/admin/list')
def admin_list():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    active_keys = {k: v for k, v in KEYS_DB.items() if v["status"] == "active"}
    return jsonify({
        "total": len(active_keys),
        "keys": active_keys
    })

@app.route('/admin/revoke')
def admin_revoke():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required"}), 400
    
    if api_key in KEYS_DB:
        KEYS_DB[api_key]["status"] = "revoked"
        return jsonify({"success": True, "message": f"Key {api_key} revoked"})
    
    return jsonify({"error": "Key not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print("""
    ╔══════════════════════════════════════╗
    ║   🔥 TW HACKER2 PUBLIC API 🔥        ║
    ║   Status: Live                       ║
    ║   Owner: @tw_hacker2                 ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port)
