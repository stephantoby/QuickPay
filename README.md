QuickPay

A secure MPesa payment platform for Mozambican merchants — accept payments online without exposing your personal phone number.

The Problem
Small merchants in Mozambique who sell online through WhatsApp, Facebook, or Instagram have no safe way to accept MPesa payments. The current process requires them to share their personal MPesa phone number publicly exposing them to fraud, impersonation, and harassment.
Customers send screenshots as proof of payment. Merchants verify manually. There is no automation, no transaction history, and no protection.

The Solution
QuickPay gives every merchant a private payment link. Customers click the link, enter their phone number and amount, and receive an MPesa prompt directly on their phone. The merchant's personal number is never seen, never shared, and never at risk.

"The merchant won't face the risk of exposing their personal MPesa number to strangers online, and won't face the risk of fraud attacks that come with sharing personal payment details publicly."


Features

Private payment links — merchant's M-Pesa number never exposed
Instant STK Push — customers receive a payment prompt on their phone
Merchant dashboard — full transaction history with revenue overview
Role-based accounts — separate merchant and customer access
JWT authentication — all protected routes require a signed token
Password hashing — Werkzeug bcrypt, plaintext never stored
No app required — works on any device with a browser


Tech Stack
Layer Technology 
Backend- Python, Flask
Database- MySQL, SQLAlchemy, Flask-Migrate
Authentication- Flask-JWT-Extended, Werkzeug
Payments- Safaricom Daraja API (MPesa STK Push)
FrontendHTML, CSS, JavaScript
Dev Tools- Postman, Ngrok, Mercurial

How It Works
1. Merchant registers and shares their payment link
2. Customer opens the link — sees no personal merchant details
3. Customer enters their phone number and amount
4. QuickPay sends an STK Push request to Safaricom Daraja API
5. Customer receives a prompt on their phone and enters their M-Pesa PIN
6. Safaricom sends a callback to QuickPay confirming the payment
7. Transaction status updates to success on the merchant dashboard

Project Structure
QuickPay/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── extensions.py        # db, migrate, jwt objects
│   ├── models.py            # SQLAlchemy data models
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py        # /register, /login, /dashboard routes
│   ├── payments/
│   │   ├── __init__.py
│   │   ├── mpesa.py         # Daraja API — token + STK Push
│   │   └── routes.py        # /pay, /callback routes
│   └── templates/           # HTML frontend pages
│       ├── homepage.html
│       ├── payment.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       └── forgot.html
├── migrations/              # Alembic migration files
├── .env.example             # Environment variable template
├── config.py                # Application configuration
├── run.py                   # Application entry point
└── requirements.txt         # Python dependencies

Database Schema
Three tables power the QuickPay system:
users — stores both merchant and customer accounts with role-based access
transactions — records every payment attempt with dual foreign keys linking both the merchant and customer involved
mpesa_callbacks — audit log storing raw Safaricom callback payloads for every STK Push result

Getting Started
Prerequisites

Python 3.11+
MySQL 8.0+
A Safaricom Daraja sandbox account
Ngrok for exposing localhost to Safaricom callbacks

Installation
1. Clone the repository
git clone https://github.com/YOURUSERNAME/QuickPay.git
cd QuickPay

2. Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

3. Install dependencies
pip install -r requirements.txt

4. Set up environment variables
cp .env.example .env

Fill in your values in .env:
MPESA_CONSUMER_KEY=your_daraja_consumer_key
MPESA_CONSUMER_SECRET=your_daraja_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_daraja_passkey
MPESA_CALLBACK_URL=https://your-ngrok-url/api/payments/callback
JWT_SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@localhost/quickpay_db

5. Create the database
CREATE DATABASE quickpay_db;

6. Run migrations
flask db upgrade

7. Start Ngrok (in a separate terminal)
ngrok http 5000
Copy the Ngrok URL and update MPESA_CALLBACK_URL in your .env, then restart Flask.

8. Run the application
flask run
Visit http://localhost:5000/api/auth/home

Testing the Payment Flow
1. Register a merchant account
jsonPOST /api/auth/register
{
  "name": "Test Merchant",
  "email": "merchant@test.com",
  "phone": "258840000001",
  "password": "test1234",
  "role": "Merchant"
}
2. Register a customer account and log in to get a JWT token
3. Open the payment page with the merchant ID
http://localhost:5000/api/payments/?merchant_id=1
4. Submit a payment using the Safaricom sandbox test number
Phone: 254708374149
Amount: 10
5. Simulate a successful callback via Postman
jsonPOST /api/payments/callback
{
  "Body": {
    "stkCallback": {
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CheckoutRequestID": "your_checkout_request_id"
    }
  }
}
6. Check the merchant dashboard — transaction shows as Success

Key Engineering Challenges
Safaricom Sandbox Instability
The Daraja sandbox returns intermittent 500/503 errors. Solved by implementing a retry loop with a 2-second backoff — attempts the STK Push up to 3 times before returning an error.
Alembic Migration Crisis
Adding the merchant_id foreign key triggered destructive DROP TABLE migrations due to __tablename__ casing mismatches between SQLAlchemy models and MySQL. Resolved by correcting all table names, using flask db stamp head to resynchronise migration state, and regenerating a clean migration.
Ngrok Domain Mismatch
Safaricom callbacks were silently failing due to a one-character difference between the .app and .io Ngrok domain in the callback URL. Identified by comparing the .env value, the Daraja portal setting, and the active Ngrok session simultaneously.

Future Works

 Emola support — Mozambique's second mobile money wallet
 QR code payments for physical merchants
 Welcome and password recovery emails via Flask-Mail
 Embeddable payment API for third-party developers
 Production deployment with live Daraja credentials
 HTTPS via Let's Encrypt


Acknowledgements
Built as a graduation project at the European University of Lefke, Faculty of Engineering, 2026.
Inspired by PaySuite — a real Mozambican payment platform.

Author
Oluwatobi Stephan Olabode
Student No: 22143468 · Computer Engineering · European University of Lefke

License
This project is licensed under the MIT License — see LICENSE for details.
