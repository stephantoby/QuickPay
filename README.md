# QuickPay

**Accept M-Pesa payments online without handing strangers your personal phone number.**

QuickPay is a Flask web application that lets merchants in Mozambique, such as Instagram sellers and small online shops, request M-Pesa payments from customers through a checkout flow. Payments are confirmed by Safaricom's callback to the server, not by screenshots or messages sent by the customer.

Built as a graduation project for the B.Sc. in Computer Engineering at the European University of Lefke (2026). Inspired by [PaySuite](https://paysuite.co.mz), a Mozambican payment platform.

> **Status:** works end to end against the Safaricom Daraja **sandbox**. It is not deployed and has not gone live with Safaricom. Deployment and production hardening are the current focus (see [Roadmap](#roadmap)).

## The problem

Merchants who sell on Instagram or their own websites usually ask customers to send money to a personal M-Pesa number. That has two costs:

- The merchant's personal number is exposed to strangers online.
- The merchant has to trust fake-able proof of payment from the customer, which opens the door to fake-payment fraud.

## How QuickPay solves it

The merchant creates a payment request. The customer gets an M-Pesa PIN prompt (STK Push) on their phone and approves it. QuickPay marks the payment as successful only when Safaricom's callback says so. QuickPay does not hold customer funds.

```mermaid
sequenceDiagram
    participant M as Merchant / checkout
    participant Q as QuickPay (Flask)
    participant D as Safaricom Daraja
    participant C as Customer phone
    M->>Q: Payment request (amount, customer phone)
    Q->>Q: Save payment as Pending
    Q->>D: STK Push request
    D-->>Q: CheckoutRequestID
    Q->>Q: Store checkout_request_id on the payment
    D->>C: M-Pesa PIN prompt
    C->>D: Customer approves
    D->>Q: Callback with result
    Q->>Q: Match checkout_request_id, set status to Successful
```

The flow is asynchronous: the response to the STK Push and the final result arrive as two separate events. The `checkout_request_id` is what links them.

## Features

- M-Pesa STK Push integration with the Safaricom Daraja API, including retry handling
- Asynchronous callback processing that links provider responses to payment records and updates transaction status (Pending / Successful)
- Merchant registration and login with JWT authentication and hashed passwords
- Payment-to-merchant linking, so each payment belongs to the merchant who requested it
- Merchant dashboard with payment charts (Chart.js)
- Database migrations with Alembic (Flask-Migrate)

## Screenshots
<img width="940" height="474" alt="image" src="https://github.com/user-attachments/assets/2f81a41a-3e8a-4949-a35e-8574188c0f41" />
<img width="940" height="501" alt="image" src="https://github.com/user-attachments/assets/fb1b0ce7-1953-4186-89a3-d93734367f01" />
<img width="940" height="504" alt="image" src="https://github.com/user-attachments/assets/8aeed1b6-fde5-43ff-b380-67efbb35f916" />

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-JWT-Extended, Werkzeug |
| Database | MySQL |
| Payments | Safaricom Daraja API (M-Pesa STK Push) |
| Frontend | HTML, CSS, JavaScript, Chart.js, Tabler Icons |
| Dev tools | ngrok (expose the local callback URL), Postman (API and callback testing) |

## Getting started

### Prerequisites

- Python 3.10 or newer
- MySQL
- [ngrok](https://ngrok.com), so Safaricom can reach your local callback URL
- A Safaricom [Daraja](https://developer.safaricom.co.ke) developer account (sandbox app)

### Setup

```bash
git clone https://github.com/stephantoby/QuickPay.git
cd QuickPay
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a MySQL database, then copy the example environment file and fill it in:

```bash
cp .env.example .env
```

```ini
# .env.example (variable names must match your config)
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me
DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost/quickpay
DARAJA_CONSUMER_KEY=
DARAJA_CONSUMER_SECRET=
DARAJA_SHORTCODE=
DARAJA_PASSKEY=
CALLBACK_URL=https://YOUR-NGROK-DOMAIN/YOUR-CALLBACK-ROUTE
```

Never commit `.env`. Run the migrations and start the app:

```bash
flask db upgrade
flask run
```

In a second terminal, expose the app so Safaricom can send callbacks:

```bash
ngrok http 5000
```

Put the HTTPS ngrok URL in `CALLBACK_URL` and restart the app.

## Testing the payment flow

Payments were tested by hand with Postman and ngrok: more than 100 test runs across payment initiation and callback handling.

- Use the Safaricom sandbox test number `254708374149`.
- The sandbox often returns result code `1037` (timeout) for this number. To test a successful payment, simulate the callback by sending the callback payload to your callback URL with Postman.
- The callback URL must exactly match the active ngrok domain. A mismatch fails silently: the STK Push succeeds but your server never receives the result.

## Security notes

- Secrets (Daraja keys, database credentials, JWT secret) are read from environment variables and are not stored in the repository.
- Passwords are hashed with Werkzeug.
- Payment status is only changed by the provider callback, never by data supplied by the customer.

## Roadmap

Development is continuing in stages:

1. **Codebase cleanup:** remove development-only routes and tidy structure
2. **Production deployment:** hosting, HTTPS (Let's Encrypt), production Daraja go-live
3. **Core missing features:** welcome email on registration, forgot-password flow, change password on the profile page
4. **Growth features**
5. **Platform features**

## Author

**Oluwatobi Stephan Olabode**
[GitHub](https://github.com/stephantoby) | [LinkedIn](https://linkedin.com/in/oluwatobi-stephan-olabode)

## License

Copyright (c) 2026 Oluwatobi Stephan Olabode. All rights reserved. The source is public for viewing and evaluation. Contact the author before reusing it.
