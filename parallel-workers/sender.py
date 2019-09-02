"""
Sender is responsible for sending the tasks to service-workers,
as messages.

NOTE: Use JSON.
      RabbitMQ has no knowladge of what the message syntax is,
      it simply transfers a byte array.
      Therefore, within Python, use a dictionary and when,
      pushing it to the MQ, convert it to a JSON string.
"""

from chunker import get_logical_chunks
from datetime import datetime
from mq_common import init_mq
import sys
import json
import logging
import pika
import os


# Set up logging.
logging.basicConfig(
    filename='sender.log',
    filemode='w',
    format='%(asctime)s - %(message)s',
    level=logging.INFO)
logging.info('Video analyzer started.')

# MQ details.
KEY = os.getenv('MQ_WORKER_QUEUE_NAME', 'worker_queue')
HOST = os.getenv('MQ_HOST', '13.127.220.123')
USERNAME = os.getenv('MQ_USERNAME', 'orchestrator')
PASSWORD = os.getenv('MQ_PASSWORD', 'orchestrator')
QUEUE = init_mq(host=HOST, name_queue=KEY, username=USERNAME, password=PASSWORD)

if QUEUE is not None:
    logging.info('Initiated connection to message queue "{queue}" at "{host}" as user "{user}".'.format(
        queue=KEY,
        host=HOST,
        user=USERNAME
    ))


video = './Fundamentals_of_Parallelism_on_Intel_Architecture+introduction.mp4'
video1 = './Fundamentals_of_Parallelism_on_Intel_Architecture+modern_code.mp4'
chunks = get_logical_chunks(video)
chunks = get_logical_chunks(video1)

for chunk in chunks:
    QUEUE.basic_publish(exchange='',routing_key=KEY, body=json.dumps(chunk, default=str))
    logging.info('Send -- {body} --> "{queue}".'.format(
        queue=KEY,
        body=json.dumps(chunk, default=str)
    ))
