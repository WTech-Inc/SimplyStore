from flask import Flask, jsonify, request, send_from_directory, render_template, session, redirect
from flask_wbank import WBankService
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import BaseForm
from wtforms.validators import DataRequired,NumberRange
from wtforms import StringField,BooleanField,SelectField,FloatField,IntegerField
import hashlib, datetime

app = Flask(__name__, template_folder="frontend")
wbank = WBankService()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://default:Gd2MsST3QYWF@ep-hidden-salad-a1a7pob9-pooler.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = hashlib.sha256("WTech2225556".encode()).hexdigest()
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=5)

@app.before_request
def br():
   session["user"] = None

product_list = [
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
  basicsalary = db.Column(db.Integer, nullable=False, default=15000)
  def __init__(self, id, name, pw, basicSalary):
    self.id = id
    self.name = name
    self.pw = pw
    self.basicsalary = basicSalary

# 訂單資料表模型
class orders(db.Model):
  __tablename__ = "orders"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  productid = db.Column(db.Integer,  db.ForeignKey("products.id"), nullable=False)
  status = db.Column(db.String(20), nullable=False, default="已付款")
  product = db.relationship("products")
  @property
  def productPrice(self):
     return self.product.price if self.product else None
  def __init__(self, id, productid, status):
    self.id = id
    self.productid = productid
    self.status = status

# Flask-Admin 視圖表單(View-Form)
class productForm(BaseForm):
  id = IntegerField('序號', validators=[DataRequired()])
  name = StringField('產品名稱', validators=[DataRequired()])
  price = IntegerField('價格(WTC$)', validators=[DataRequired()])
  stock = IntegerField('庫存', validators=[DataRequired()])

class staffForm(BaseForm):
  id = IntegerField('序號', validators=[DataRequired()])
  name = StringField('員工名稱', validators=[DataRequired()])
  pw = StringField('登入密碼', validators=[DataRequired()])
  basicsalary = IntegerField('底薪(WTC$)', validators=[DataRequired()])

class orderForm(BaseForm):
  id = IntegerField('序號', validators=[DataRequired()])
  productid = StringField('訂購物品序號(可從產品表看)', validators=[DataRequired()])
  status = SelectField('訂單狀態', choices=[], validators=[DataRequired()])
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.status.choices = [('', ''), ('等待付款', '用戶未付款'), ('已付款、採購產品中', '你需要購買產品'), ('已完成', '完成訂單')]
  
# Flask-Admin 視圖(View)
class productView(ModelView):
  column_display_pk=True
  column_searchable_list = ('name', 'id')
  column_labels = {
        'id': '產品序號',
        'name': '產品名',
        'price': '價格(WTC$)',
        'stock': '庫存'
  }
  edit_modal=True
  form = productForm
  def is_accessible(self):
    return True
  def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not
        accessible.
        """
        if not self.is_accessible(): return redirect("/admin/login")

class staffView(ModelView):
  column_display_pk=True
  column_searchable_list = ('name', 'id')
  column_labels = {
        'id': '員工序號',
        'name': '員工名',
        'pw': '登入密碼',
        'basicsalary': '底薪(WTC$)'
  }
  edit_modal=True
  form = staffForm
  def is_accessible(self):
    return True
  def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not
        accessible.
        """
        if not self.is_accessible(): return redirect("/admin/login")

class orderView(ModelView):
  column_display_pk=True
  column_list = ('id', 'productid', 'status')
  column_searchable_list = ('id', 'status')
  column_labels = {
        'id': '訂單序號',
        'productid': '產品序號（可從表看)',
        'status': '訂單狀態'
  }
  edit_modal=True
  form = orderForm
  def is_accessible(self):
    return True
  def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not
        accessible.
        """
        if not self.is_accessible(): return redirect("/admin/login")

# Flask-Admin
admin = Admin(app, name='線上商城--管理介面', template_mode='bootstrap4')
admin.add_view(productView(products, db.session, name="產品管理"))
admin.add_view(staffView(staff, db.session, name="人員管理"))
admin.add_view(orderView(orders, db.session, name="訂單管理"))

with app.app_context():
   db.create_all()

# 路由Route
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
  if request.method == "GET": return render_template("login.html")
  else:
    user = request.form.get("uname")
    pw = request.form.get("pw")
    if not user:
      return redirect("/admin/login")
    if not pw:
      return redirect("/admin/login")
    users = staff.query.filter_by(name=user).first()
    if users:
      session["user"] = {"uname":users.name, "pw":users.pw}
      return redirect("/admin")
    return redirect("/admin/login")

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/products")
def product():
  query = db.session.execute(text("select * from products")).fetchall()
  if len(query) == 0: return jsonify(pname="沒有", price=20, stock=0)
  result = [{'pname': record[1], 'price': record[2], 'stock': record[3]} for record in query]
  return jsonify(result)

@app.route('/wbank/pay', methods=['POST'])
def wbank_pay():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    amount = data.get("amount")
    if not username or not password or not amount:
        return jsonify({"success": False, "message": "Missing credentials or amount"}), 400
    result = wbank.process_payment(username, password, amount)
    if result["success"]:
      product = products.query.filter_by(price=amount).first()
      os = orders.query.all()
      order = orders(id=len(os)+1, productid=product.id, status="已付款")
      db.session.add(order)
      db.session.commit()
      return jsonify(result)
    return jsonify(result)

app.run(port=4455)