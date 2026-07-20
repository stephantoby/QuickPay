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

