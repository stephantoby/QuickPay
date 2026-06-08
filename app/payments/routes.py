import uuid
from flask import Blueprint, request, jsonify, render_template
from ..extensions import db
from ..models import Transaction,MpesaCallback
from .mpesa import MpesaClient
from flask_jwt_extended import jwt_required, get_jwt_identity

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/")
def home():
    return render_template("payment.html")


@payments_bp.route("/pay", methods=["POST"])
@jwt_required()#This protection handles fake requests 
def pay():
    customer_id = get_jwt_identity()
    phone = request.form.get("phone")
    amount = request.form.get("amount")
    merchant_id = request.form.get("merchant_id")

    # Validate phone number
    if not phone or not phone.isdigit() or len(phone) < 9:
        return jsonify({"error": "Invalid phone number"}), 400

    # Error handling so the code doesnt crash! // Specific errors we can handle 
    try: 
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    
    transaction_id = str(uuid.uuid4()) #Generates a unique id for the payment attempt for callback identification

    transaction = Transaction(#creates a record before stk push 
        customer_phone=phone,   
        amount=amount,
        status="pending",
        transaction_id=transaction_id,
        merchant_id=int(merchant_id),
        customer_id=int(customer_id)
    )
    db.session.add(transaction)
    db.session.commit()


    mpesa = MpesaClient()
    #trigger STK push by building a payload
    mpesa_response = mpesa.stk_push(
        phone=phone,
        amount=amount,
        reference=transaction_id
    )
    print("MPESA RESPONSE:", mpesa_response)


    checkout_id = mpesa_response.get("CheckoutRequestID") 
    if checkout_id:
        transaction.mpesa_checkout_id = checkout_id
        db.session.commit()

    return jsonify({
        "message": "Payment request sent!",
        "transaction_id": transaction_id,
        "status": "pending"
    }), 200

#Route responsible for changing status 
@payments_bp.route("/status/<transaction_id>", methods=["GET"])
def payment_status(transaction_id):
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first_or_404()
    
    return jsonify({
        "transaction_id": transaction_id,
        "status":transaction.status
    }), 200

 # Mpesa API calls this URL after the user accepts or rejects payment

@payments_bp.route("/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()

    stk_callback = data["Body"]["stkCallback"]
    result_code = stk_callback["ResultCode"]
    checkout_id = stk_callback["CheckoutRequestID"]

    transaction = Transaction.query.filter_by(
        mpesa_checkout_id=checkout_id
    ).first()

    if not transaction:
        transaction = Transaction.query.filter_by(
        status="pending"
    ).order_by(Transaction.created_at.desc()).first()

    if transaction:
        transaction.status = "success" if result_code == 0 else "failed"
        db.session.commit()

    callback_record = MpesaCallback(
    transaction_id=transaction.transaction_id if transaction else None,
    result_code=result_code,
    result_desc=stk_callback.get("ResultDesc"),
    raw_payload=str(data),
    )
    db.session.add(callback_record)
    db.session.commit()    


    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200
