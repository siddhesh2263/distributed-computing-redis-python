import os
import random
from datetime import datetime
from json import dumps
from time import sleep
from uuid import uuid4
import redis
from flask import Flask, request, jsonify


# Access Redis config values:
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME")
REDIS_DB_NUMBER = int(os.getenv("REDIS_DB_NUMBER"))

# Connect to Redis:
def redis_db():
    db = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB_NUMBER,
        decode_responses=True,
    )

    # Make sure Redis is up and running:
    db.ping()

    return db

def redis_queue_push(db, message):
    # Push to tail of the queue (left of the list):
    db.lpush(REDIS_QUEUE_NAME, message)

def main(num_messages: int, delay: float = 1):
    """
    Generates `num_messages` and pushes them to a Redis queue
    :param num_messages:
    :return:
    """

    # Connect to Redis:
    db = redis_db()

    for i in range(num_messages):
        # Create message data:
        message = {
            "id": str(uuid4()),
            "ts": datetime.utcnow().isoformat(),
            "data": {
                "message_number": i,
                "x": random.randrange(0, 100),
                "y": random.randrange(0, 100),
            },
        }

        # We will store the data as JSON in Redis:
        message_json = dumps(message)

        # Push message to Redis queue:
        print(f"Sending message {i + 1} (id={message['id']})")
        redis_queue_push(db, message_json)

        # Wait a bit so we have time to start up workers and see
        # how things interact:
        sleep(delay)

app = Flask(__name__)

@app.route("/dispatch", methods=["POST"])
def dispatch():
    print("Inside dispatch")
    """
    Example:
    curl -X POST http://HOST:8000/dispatch \
           -H "Content-Type: application/json" \
           -d '{"count": 30, "delay": 0.1}'
    """
    body = request.get_json(force=True, silent=False)   # If not valid JSON body, return 400 bad request.
    num_messages = int(body.get("num_messages", 1))
    delay = float(body.get("delay", 0.1))
    main(num_messages, delay)
    return jsonify({"status": "queued", "num_messages": num_messages, "delay": delay}), 200

# if __name__ == "__main__":
#     # 30 messages with a delay of 0.1 seconds:
#     main(30, 0.1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)