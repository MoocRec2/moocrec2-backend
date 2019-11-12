from datetime import datetime
from mq_common import init_mq
from time import time
import random
import json
import os
import subprocess

def get_hostname():
    """
    Returns the hostname of the running machine. Use this to identify a worker using,
    Docker container id if Docker is used.
    """
    output = subprocess.Popen('hostname', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = output.communicate()

    if stderr is not None:
        return { 'Successful': False, 'Output': stderr }
    else:
        return { 'Successful': True, 'Output': stdout.decode('ASCII').replace('\n', '')}



def on_message(channel, method, properties, body):
    print(json.loads(body))

WORKER_KEY = os.getenv('MQ_WORKER_QUEUE_NAME', 'worker_queue')
ANALYZER_KEY = os.getenv('MQ_ANALYZER_QUEUE_NAME', 'analyzer_queue')
HOST = os.getenv('MQ_HOST', '13.127.220.123')
USERNAME = os.getenv('MQ_USERNAME', 'worker')
PASSWORD = os.getenv('MQ_PASSWORD', 'worker')
VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY', '/tmp')

WORKER_QUEUE = init_mq(
    host=HOST, name_queue=WORKER_KEY, username=USERNAME, password=PASSWORD)
ANALYZER_QUEUE = init_mq(
    host=HOST, name_queue=ANALYZER_KEY, username=USERNAME, password=PASSWORD)


# Get a random worker_id. If this is running on Docker, container id will be random.
hostname = get_hostname()
WORKER_ID = hostname['Output'] if hostname['Successful'] else str(int(time())) + str(random.randint(0, 9))


# Prep for consuming.
print('Worker', WORKER_ID, 'started.\n\n')
# We only acknowladge the message after the task is complete,
# This ensures that the message remains in the qeueu even if the,
# worker crashes during processing.
WORKER_QUEUE.basic_consume(
    queue=WORKER_KEY, auto_ack=False, on_message_callback=on_message)
# Start.
WORKER_QUEUE.start_consuming()