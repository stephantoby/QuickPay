import requests, time, base64
from datetime import datetime
from flask import current_app  

class MpesaClient: 
    def get_access_token(self):#This function fetches token from safaricom
        consumer_key= current_app.config["MPESA_CONSUMER_KEY"]
        consumer_secret= current_app.config["MPESA_CONSUMER_SECRET"]

        response = requests.get("https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
                                auth=(consumer_key, consumer_secret))
        
        print("TOKEN RESPONSE STATUS:", response.status_code)
        print("TOKEN RESPONSE BODY:", response.text)

        token = response.json().get("access_token") #extracts the token from safaricom json response
        return token
    
    def stk_push(self, phone, amount, reference):
        access_token = self.get_access_token()
        
        shortcode = current_app.config["MPESA_SHORTCODE"]
        passkey = current_app.config["MPESA_PASSKEY"]
        callback_url = current_app.config["MPESA_CALLBACK_URL"]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

#This is how safaricom verifies if the request is legit 
#safari does the same calculation on their side to compare 
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode() 

#JSON body safari expects 
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber" : phone,
            "CallBackURL": callback_url,
            "AccountReference": reference,
            "TransactionDesc": "Quickpay Payment"
        }
#Retry logic
        for attempt in range(3):
            response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
            print("STK RESPONSE STATUS:", response.status_code)
            print("STK RESPONSE BODY:", response.text)
            
            if response.status_code == 200:
                break
            
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)

        try:
            return response.json()
        except Exception:
            return {"error": "Empty response", "status_code": response.status_code, "raw": response.text}