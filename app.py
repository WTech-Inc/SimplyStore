from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_wbank import WBankService

app = Flask(__name__, static_folder="../frontend")
wbank = WBankService()

products = [
  dict(id=1, name="wbank-30000", price=300),
  dict(id=2, name="protein-55g", price=120)
]

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/products")
def product():
  return jsonify(products)

@app.route('/wbank/pay', methods=['POST'])
def wbank_pay():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")
    if not username or not password or not amount:
        return jsonify({"success": False, "message": "Missing credentials or amount"}), 400
    result = wbank.process_payment(username, password, amount)
    return jsonify(result)
