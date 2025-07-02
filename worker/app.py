import os
import redis
from json import loads
import random

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

def redis_queue_pop(db):
    # Pop from head of the queue (right of the list).
    # The `b` in `brpop` indicates that this is a blocking call,
    # (it waits until an item becomes available.)
    # If there is no message in the queue, the worker should wait.
    # Since there are multiple workers, one of the workers will block
    # the call to the redis queue.
    # SQS doesn't guarentee that a message cannot be delivered more
    # than once. In Redis, we shouldn't run into this issue. (this
    # is when we want to check based on message ID, if the message
    # is processed or not, not concerned here.)
    # So, we are blocking the pop until there is something 
    # available to pop.
    _, message_json = db.brpop(REDIS_QUEUE_NAME)
    return message_json

def process_message(db, message_json: str):
    message = loads(message_json)
    print(f"Message received: id={message['id']}, message_number={message['data']['message_number']}")

    # mimic potential processing errors:
    processed_ok = random.choices((True, False), weights=(5, 1), k=1)[0]
    if processed_ok:
        print(f"\tProcessed successfully")
    else:
        print(f"\tProcessing failed - requeuing...")
        redis_queue_push(db, message_json)

def main():
    """
    Consumes items from the Redis queue
    """
    # Connect to Redis:
    db = redis_db()

    while True:
        message_json = redis_queue_pop(db)
        process_message(db, message_json)

if __name__ == '__main__':
    main()