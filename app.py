from flask import Flask, request, jsonify
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
from google.cloud import storage


app = Flask(__name__)

@app.route("/", methods=["POST"])
def chat_webhook():
    event = request.json
    
    attachment=event["chat"]["messagePayload"]["message"]["attachment"]
    
    resource_name=attachment[0]["name"]
        
    
    SCOPES = ["https://www.googleapis.com/auth/chat.bot"]
    SERVICE_ACCOUNT_FILE = "snapfit-9efb-71568e26bf3f.json"

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    chat = build("chat", "v1", credentials=creds)
    
    attachment = chat.spaces().messages().attachments().get(name=resource_name).execute()

    media_resource = attachment["attachmentDataRef"]["resourceName"]

    download_request = chat.media().download_media(
        resourceName=media_resource
    )  

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, download_request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print("Download %d%%." % int(status.progress() * 100))
            
    fh.seek(0)

    client = storage.Client.from_service_account_json("snapfit-9efb-71568e26bf3f.json")

    bucket = client.bucket("gchat-image-dump")
    blob = bucket.blob("images/downloaded.jpg")
    blob.upload_from_file(fh, rewind=True,content_type="image/jpeg")

    print(f"✅ Uploaded to gs://gchat-image-dump")
        
    return "gs://gchat-image-dump/images/"
    
    
    
    

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
