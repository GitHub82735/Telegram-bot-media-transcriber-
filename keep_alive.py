from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot-ka waa nool yahay!"

def run():
    app.run(host='0.0.0.0', port=8080)

def ping_itself():
    # Only log without attempting to ping to avoid errors
    while True:
        try:
            print("Keep-alive service is running...")
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            print(f"Keep-alive error: {e}")

def keep_alive():
    t1 = Thread(target=run)
    t2 = Thread(target=ping_itself)
    t1.start()
    t2.start()