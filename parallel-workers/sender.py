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
import pika
import os


# MQ details.
KEY = os.getenv('MQ_WORKER_QUEUE_NAME', 'mq')
HOST = os.getenv('MQ_HOST', '13.235.16.166')
USERNAME = os.getenv('MQ_USERNAME', 'worker')
PASSWORD = os.getenv('MQ_PASSWORD', 'worker')
QUEUE = init_mq(host=HOST, name_queue=KEY, username=USERNAME, password=PASSWORD)

video = '/Users/anushka/CDAP/moocrec2-backend/parallel-workers/video.mp4'
chunks = get_logical_chunks(video)

for chunk in chunks:
    QUEUE.basic_publish(exchange='',routing_key=KEY, body=json.dumps(chunk, default=str))
