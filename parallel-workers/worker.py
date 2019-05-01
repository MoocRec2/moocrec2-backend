"""
A service-worker, responsible for intercepting a message,
from message queue and acting on it.

NOTE: Use JSON.
      RabbitMQ has no knowladge of what the message syntax is,
      it simply transfers a byte array.
      Therefore, within Python, convert the JSON string in the message,
      to a dictionary.
"""

from datetime import datetime
from mq_common import init_mq
import random
import logging
import json
import os

# MQ details.
KEY = os.getenv('MQ_NAME', 'mq')
HOST = os.getenv('MQ_HOST', 'localhost')
USERNAME = os.getenv('MQ_USERNAME', 'worker')
PASSWORD = os.getenv('MQ_PASSWORD', 'worker')
QUEUE = init_mq(host=HOST, name_queue=KEY, username=USERNAME, password=PASSWORD)
WORKER_ID = random.randint(0, 9)

# Logging set up.
logging.basicConfig(filename='worker.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('Worker ' + str(WORKER_ID) + ' started at ' + str(datetime.utcnow().isoformat()))

def on_message(channel, method, properties, body):
    # Convert to dictionary.
    message = ''

    try:
        message = json.loads(body)
    except ValueError:
        message = body

    logging.info('Worker Id:\t' + str(WORKER_ID) + '\nMessage:\n' + str(message) + '\n')
    # Send acknowladgement.
    channel.basic_ack(delivery_tag=method.delivery_tag)


# Prep for consuming.
print ('Worker', WORKER_ID, 'started.\n\n')
# We only acknowladge the message after the task is complete,
# This ensures that the message remains in the qeueu even if the,
# worker crashes during processing.
QUEUE.basic_consume(queue=KEY, auto_ack=False, on_message_callback=on_message)
# Start.
QUEUE.start_consuming()