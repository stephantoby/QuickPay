from datetime import datetime
from .extensions import db

class Users(db.Model):#inherits model features that allow me to use the class as a db (querying, commit)
    __tablename__ = "users" #tell sql alquemy which mysql table this class maps to.

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable= False)
    phone = db.Column(db.String(20), unique = True, nullable = False )
    password_hash = db.Column(db.String(255), nullable = False)
    role = db.Column(db.Enum("Customer", "Merchant"), default = "Customer")
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    bi_number = db.Column(db.String(20), nullable=True)

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key= True)
    customer_phone = db.Column(db.String(20), nullable = False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable= True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable = False )
    status = db.Column(db.Enum("pending", "success", "failed", default = "pending"))
    transaction_id = db.Column(db.String(100), unique = True, nullable = False)
    mpesa_checkout_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, default = datetime.utcnow, onupdate= datetime.utcnow)

class MpesaCallback(db.Model):#stores the unmodified response from safari
    __tablename__ = "mpesa_callbacks"
    
    id = db.Column(db.Integer, primary_key = True)
    transaction_id = db.Column(db.String(100),db.ForeignKey("transactions.transaction_id"))
    result_code = db.Column(db.Integer)
    result_desc = db.Column(db.String(255))
    raw_payload = db.Column(db.Text)
    received_at = db.Column(db.DateTime, default = datetime.utcnow)


