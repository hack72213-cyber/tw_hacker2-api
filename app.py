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
    KEYS_DB[api_key] = {"customer": customer, "expires": expires.isoformat(), "status": "active"}
    return api_key

def check_key(api_key):
    if api_key not in KEYS_DB: return None
    if KEYS_DB[api_key]["status"] != "active": return "revoked"
    if datetime.now() > datetime.fromisoformat(KEYS_DB[api_key]["expires"]): return "expired"
    return KEYS_DB[api_key]

@app.route('/')
def home():
    return jsonify({"service": "TW HACKER2 API", "owner": "@tw_hacker2", "status": "Live"})

@app.route('/api/user')
def get_user():
    api_key = request.args.get('api_key')
    if not api_key: return jsonify({"error": "api_key required"}), 401
    result = check_key(api_key)
    if not result or result in ["expired", "revoked"]: return jsonify({"error": "Invalid key"}), 401
    term = request.args.get('term')
    if not term: return jsonify({"error": "term required"}), 400
    r = requests.get(f"https://users-xinfo-admin.vercel.app/api?key=demo&type=user&term={term}")
    return jsonify(r.json())

@app.route('/api/mobile')
def get_mobile():
    api_key = request.args.get('api_key')
    if not api_key: return jsonify({"error": "api_key required"}), 401
    result = check_key(api_key)
    if not result or result in ["expired", "revoked"]: return jsonify({"error": "Invalid key"}), 401
    term = request.args.get('term')
    if not term: return jsonify({"error": "term required"}), 400
    r = requests.get(f"https://users-xinfo-admin.vercel.app/api?key=demo&type=mobile&term={term}")
    return jsonify(r.json())

@app.route('/admin/gen')
def admin_gen():
    if request.args.get('admin_key') != ADMIN_KEY: return jsonify({"error": "Unauthorized"}), 401
    customer = request.args.get('customer')
    days = request.args.get('days', '7')
    if not customer: return jsonify({"error": "customer required"}), 400
    key = generate_key(customer, days)
    return jsonify({"api_key": key, "customer": customer, "expires": KEYS_DB[key]["expires"]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
