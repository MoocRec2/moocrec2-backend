"""
Sender is responsible for sending the tasks to service-workers,
as messages.

NOTE: Use JSON.
      RabbitMQ has no knowladge of what the message syntax is,
      it simply transfers a byte array.
      Therefore, within Python, use a dictionary and when,
      pushing it to the MQ, convert it to a JSON string.
"""

from datetime import datetime
from mq_common import init_mq
import sys
import json
import pika
import os


# MQ details.
KEY = os.getenv('MQ_NAME', 'mq')
HOST = os.getenv('MQ_HOST', 'localhost')
USERNAME = os.getenv('MQ_USERNAME', 'worker')
PASSWORD = os.getenv('MQ_PASSWORD', 'worker')
QUEUE = init_mq(host=HOST, name_queue=KEY, username=USERNAME, password=PASSWORD)

# Sending 5 messages.
for i in range(1,20):
    print (i)
    message = { 'id': i, 'time': datetime.utcnow() }
    QUEUE.basic_publish(exchange='',routing_key=KEY, body=json.dumps(message, default=str))

