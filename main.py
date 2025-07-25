
import time
from flask import Flask
import Data_Ingestion_Gmail

app = Flask(__name__)

@app.route('/')
def index():
    return "Gmail watcher is running!"

def watch_gmail():
    service = Data_Ingestion_Gmail.authenticate()
    while True:
        print("GMail watcher is active.")
        print("Checking for new receipts...")
        receipts = Data_Ingestion_Gmail.fetch_receipts(service)
        if receipts:
            print(f"Found {len(receipts)} new receipt-like emails.")
            for msg in receipts:
                print("==========")
                print(Data_Ingestion_Gmail.extract_text(service, msg['id']))
                print("==========")
        time.sleep(3000) # Check every 5 minutes

if __name__ == '__main__':
    import threading
    gmail_thread = threading.Thread(target=watch_gmail)
    gmail_thread.start()
    app.run(port=8080)