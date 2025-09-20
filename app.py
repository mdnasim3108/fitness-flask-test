from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def chat_webhook():
    event = request.json
    print("Event received:", event)

    # Example: respond back with a message
    if "message" in event:
        user_text = event["message"].get("text")
        return jsonify({"text": f"You said: {user_text}"})
    
    return "OK"

@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
