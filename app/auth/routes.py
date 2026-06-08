from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Users, Transaction
import secrets, string


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register(): #Server sends json request out to the users browser 
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    role = data.get("role","Customer")

    if not all([name, email, phone, password]):  
        return jsonify({"error": "All fields are required"}), 400 #Bad request
    
    #Checks the database to prevent duplicate accounts 
    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    if Users.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone already registered"}), 400
    
    hashed_password = generate_password_hash(password)

    user = Users(  #Created a users object 
        name = name,
        email = email,
        phone = phone, 
        password_hash = hashed_password,
        role = role
    )

    db.session.add(user)
    db.session.commit()
    

    return jsonify({"message": "Account created successfully"}), 201 #Created a new record 

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):#if at least one is empty it all() returns false 
        return jsonify({"error": "Email and password are required"}), 400
    
    user = Users.query.filter_by(email=email).first() 

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401#Unauthorized 
    
    token = create_access_token(identity=str(user.id))

    return jsonify({
    "token": token,
    "user":{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role
    }
}), 200

@auth_bp.route("/dashboard", methods=["GET"])
@jwt_required() #Proctecting the route 
def dashboard():
    user_id = get_jwt_identity()

    user = Users.query.get(int(user_id))

    if not user or user.role != "Merchant":
        return jsonify({"error": "Access denined - merchants only"}), 403 #Forbidden 
    
    transactions = Transaction.query.filter_by(merchant_id= int(user_id)).all()

    history = []
    for t in transactions:
        history.append({
            "transaction_id": t.transaction_id,
            "customer_phone": t.customer_phone,
            "amount": str(t.amount),
            "status": t.status,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "merchant": user.name,
        "total_transactions": len(history),
        "transactions": history 
    }), 200

@auth_bp.route("/customer-dashboard", methods=["GET"])
@jwt_required()
def customer_dashboard():
    user_id = get_jwt_identity()

    user = Users.query.get(int(user_id))

    if not user or user.role != "Customer":
        return jsonify({"error": "Access denied - customers only"}), 403

    transactions = Transaction.query.filter_by(customer_id=int(user_id)).all()

    history = []
    for t in transactions:
        history.append({
            "transaction_id": t.transaction_id,
            "customer_phone": t.customer_phone,
            "amount": str(t.amount),
            "status": t.status,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "customer": user.name,
        "total_transactions": len(history),
        "transactions": history
    }), 200

@auth_bp.route("/login-page")
def login_page():
    return render_template('login.html')

@auth_bp.route("/dashboard-page")
def dashboard_page():
    return render_template('dashboard.html')

@auth_bp.route("/register-page")
def register_page():
    return render_template('register.html')

@auth_bp.route("/home")
def home_page():
    return render_template('homepage.html')

@auth_bp.route("/update-bi", methods=["POST"]) #For kyc verification 
@jwt_required()
def update_bi():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))

    if not user or user.role != "Customer":
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    bi_number = data.get("bi_number")

    if not bi_number:
        return jsonify({"error": "BI number is required"}), 400

    user.bi_number = bi_number
    db.session.commit()

    return jsonify({"message": "BI number updated successfully"}), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    phone = data.get("phone")

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    user = Users.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({"error": "No account found with that phone number"}), 404 #Not found

    # Generate temporary password
    chars = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(chars) for _ in range(8))

    user.password_hash = generate_password_hash(temp_password)
    db.session.commit()

    return jsonify({
        "message": "Temporary password generated",
        "temp_password": temp_password
    }), 200

@auth_bp.route("/forgot-page")
def forgot_page():
    return render_template('forgot.html')