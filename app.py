from flask import Flask, request, jsonify
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
from google.cloud import storage
from google.auth import default

app = Flask(__name__)

@app.route("/", methods=["POST"])
def chat_webhook():
    event = request.json

    attachment = event["chat"]["messagePayload"]["message"]["attachment"]
    resource_name = attachment[0]["name"]

    # Get default credentials automatically from Cloud Run's service account
    creds, project = default(scopes=["https://www.googleapis.com/auth/chat.bot"])
    chat = build("chat", "v1", credentials=creds)

    # Get the attachment metadata
    attachment = chat.spaces().messages().attachments().get(name=resource_name).execute()
    media_resource = attachment["attachmentDataRef"]["resourceName"]

    # Download the media
    download_request = chat.media().download_media(resourceName=media_resource)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, download_request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download {int(status.progress() * 100)}%.")

    fh.seek(0)

    # Use Cloud Run's service account automatically
    client = storage.Client()
    bucket = client.bucket("gchat-image-dump")
    blob = bucket.blob("images/downloaded.jpg")
    blob.upload_from_file(fh, rewind=True, content_type="image/jpeg")

    print("✅ Uploaded to gs://gchat-image-dump")

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
