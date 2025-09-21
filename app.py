from flask import Flask, request, jsonify
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession


app = Flask(__name__)

@app.route("/", methods=["POST"])
def chat_webhook():
    event = request.json
    
    attachment=event["chat"]["messagePayload"]["message"]["attachment"]
    
    resource_name=attachment[0]["attachmentDataRef"]["resourceName"]
    
    attachment_url = f"https://chat.googleapis.com/v1/{resource_name}?alt=media"
    
    
    SCOPES = ["https://www.googleapis.com/auth/chat.bot"]
    SERVICE_ACCOUNT_FILE = "snapfit-9efb-1081c5d4c2ee.json"

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    authed_session = AuthorizedSession(creds)

    resp = authed_session.get(attachment_url)

    if resp.status_code == 200:
        with open("image.png", "wb") as f:
            f.write(resp.content)
        print("Image downloaded successfully")
    else:
        print("Failed:", resp.status_code, resp.text)   

    return jsonify({"text": f"We got your image in our system"})
        
    
    
    
    

@app.route("/test", methods=["POST"])
def webhook():
    data = request.json   # parses JSON body
    print("📩 Received POST payload:", data)
    return "OK", 200

@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
