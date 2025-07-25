import json
from flask import Flask, request, jsonify
import Data_Ingestion_Gmail
import base64
import os

app = Flask(__name__)

# Pub/Sub and GCP info
PUBSUB_TOPIC = 'projects/agenticai-467004/topics/AgenticAI-Gmail-pushnotifications'
GCP_PROJECT_ID = 'agenticai-467004'

# File to store last historyId
HISTORY_FILE = 'last_history_id.txt'

def get_last_history_id():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return f.read().strip()
    return None

def set_last_history_id(history_id):
    with open(HISTORY_FILE, 'w') as f:
        f.write(str(history_id))


@app.route('/')
def index():
    return "Gmail watcher is running and listening for push notifications!"


@app.route('/gmail_push', methods=['POST'])
def gmail_push():
    """Handler for incoming Gmail push notifications."""
    try:
        envelope = json.loads(request.data.decode('utf-8'))
        if not envelope.get('message'):
            return 'Invalid message format', 400

        pubsub_message = envelope['message']

        if not pubsub_message.get('data'):
            return 'No data in message', 400

        # Decode base64 message data
        data = base64.b64decode(pubsub_message['data']).decode('utf-8')
        message_data = json.loads(data)

        user_id = message_data.get('emailAddress')
        history_id = message_data.get('historyId')

        if not user_id:
            return 'User ID not found in message', 400

        print(f"Received push notification for user: {user_id}, historyId: {history_id}")

        service = Data_Ingestion_Gmail.authenticate()

        # Incremental fetch using historyId
        last_history_id = get_last_history_id()

        if last_history_id:
            print(f"Fetching changes since historyId: {last_history_id}")
            history = service.users().history().list(
                userId='me',
                startHistoryId=last_history_id,
                historyTypes=['messageAdded'],
                labelId='INBOX'
            ).execute()

            messages = []
            if 'history' in history:
                for record in history['history']:
                    for msg in record.get('messagesAdded', []):
                        messages.append(msg['message'])

            print(f"Found {len(messages)} new messages.")
            for msg in messages:
                print("==========")
                print(Data_Ingestion_Gmail.extract_text(service, msg['id']))

        else:
            print("No last historyId found — skipping incremental fetch.")

        # Update stored historyId to the latest one received
        if history_id:
            set_last_history_id(history_id)

        return 'OK', 200

    except Exception as e:
        print(f"Error processing push notification: {e}")
        return 'Error', 500


def watch_gmail():
    """Sets up the Gmail watch request."""
    service = Data_Ingestion_Gmail.authenticate()
    try:
        request_body = {
            'topicName': PUBSUB_TOPIC,
            'labelIds': ['INBOX'],
            'labelFilterAction': 'include'
        }
        response = service.users().watch(userId='me', body=request_body).execute()
        print(f"Gmail watch established: {response}")

        # Store the initial historyId so we can fetch new messages later
        if 'historyId' in response:
            set_last_history_id(response['historyId'])

    except Exception as e:
        print(f"Error setting up Gmail watch: {e}")


if __name__ == '__main__':
    import threading
    gmail_watch_thread = threading.Thread(target=watch_gmail)
    gmail_watch_thread.start()

    app.run(port=8080)
