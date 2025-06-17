import requests
import json
import hashlib
import logging

class WBankService:
    def __init__(self):
        self.auth_url = "https://wtechhk.com/wbank/v2/csrftoken"
        self.session_url = "https://wtechhk.com/wbank/auth/v1/session"
        self.action_url = "https://wtechhk.com/wbank/card/action"
        self.bearer_token = "wtech666"
    
    def get_csrf_token(self):
        try:
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            response = requests.get(url=self.auth_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get("token")
            else:
                logging.error(f"Failed to get CSRF token: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Error getting CSRF token: {str(e)}")
            return None
    
    def authenticate_session(self, username, password, csrf_token):
        try:
            data = {
                "user": username,
                "pw": password,
                "url": "/wbank/card/action",
                "csrf_token": csrf_token
            }
            response = requests.get(url=self.session_url, data=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Authentication failed: {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Error during authentication: {str(e)}")
            return None
    
    def process_payment(self, username, password, amount):
        try:
            csrf_token = self.get_csrf_token()
            if not csrf_token:
                return {"success": False, "message": "無法獲取認證令牌"}
            session_data = self.authenticate_session(username, password, csrf_token)
            if not session_data:
                return {"success": False, "message": "認證失敗，請檢查用戶名和密碼"}
            payment_data = session_data.copy()
            payment_data["password"] = payment_data.get("loginPw", password)
            payment_data["cardNumber"] = hashlib.sha256(
                f"{payment_data.get('accnumber', '')}->{payment_data['password']}".encode("utf-8")
            ).hexdigest()
            payment_data["accessKey"] = "12309"
            payment_data["reviewer"] = "wbank"
            payment_data["amount"] = str(int(amount))
            response = requests.patch(url=self.action_url, json=payment_data, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                return {
                    "success": True, 
                    "message": "付款成功",
                    "new_balance": response_data.get("balance", 0)
                }
            else:
                logging.error(f"Payment failed: {response.status_code}")
                return {"success": False, "message": "付款失敗，請稍後再試"}
        except Exception as e:
            logging.error(f"Error processing payment: {str(e)}")
            return {"success": False, "message": "處理付款時發生錯誤"}
