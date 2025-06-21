from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_wbank import WBankService
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__, static_folder="../frontend")
wbank = WBankService()
app.config['SQLALCHEMY_DATABASE_URI'] = str(os.environ.get("dataurl"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = hashlib.sha256("WTech2225556".encode()).hexdigest()

products = [
  dict(id=1, name="wbank-30000", price=300),
  dict(id=2, name="protein-55g", price=120)
]

db = SQLAlchemy(app)

# 產品資料表模型
class products(db.Model):
  __tablename__ = "products"
  id = db.Column(db.Integer, primary_key=True, autoincrement=False)
  name = db.Column(db.String(80), nullable=False)
  price = db.Column(db.Integer, nullable=False)
  stock = db.Column(db.Integer, nullable=False)
  def __init__(self, id, name, price, stock):
    self.id = id
    self.name = name
    self.price = price
    self.stock = stock

# 員工資料表模型
class staff(db.Model):
  __tablename__ = "staff"
  id = db.Column(db.Integer, primary_key=True, autoincrement=False)
  name = db.Column(db.String(20), nullable=False)
  pw = db.Column(db.String(30), nullable=False, default="wtech1234")
  basicSalary = db.Column(db.Integer, nullable=False, default=15000)
  def __init__(self, id, name, pw, basicSalary):
    self.id = id
    self.name = name
    self.pw = pw
    self.basicSalary = basicSalary

# 訂單資料表模型
class orders(db.Model):
  __tablename__ = "orders"
  id = db.Column(db.Integer, primary_key=True, autoincrement=False)
  productName = db.Column(db.String(80), db.ForeignKey("products.name"), nullable=False)
  productPrice = db.Column(db.Integer, db.ForeignKey("products.price"), nullable=False)
  status = db.Column(db.String(20), nullable=False, default="等待付款")
  def __init__(self, id, productName, productPrice, status):
    self.id = id
    self.productName = productName
    self.productPrice = productPrice
    self.status = status
    
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
