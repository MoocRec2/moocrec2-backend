"""
A service-worker, responsible for intercepting a message,
from message queue and acting on it.

In this case, a worker will analyze a video file mentioned,
in the message.

NOTE: Use JSON.
      RabbitMQ has no knowladge of what the message syntax is,
      it simply transfers a byte array.
      Therefore, within Python, convert the JSON string in the message,
      to a dictionary.
"""
from datetime import datetime
from mq_common import init_mq
from time import time
from classifier import videoStyles
import random
import json
import os
import sys
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


def absolute_path(directory: str, filename: str) -> str:
    """
    Creates an absolute path to a file based on the file name and the directory.
    This is rather trivial and is used to get the absolute path without any additional /

    :param directory
        Path to the directory in which the file is.
    :param filename
        Name of the file.

    :returns str
        Absolute path to the file.
    """

    # Verify directory path and format it.
    if not directory.endswith('/'):
        directory = directory + '/'
    if not directory.startswith('/'):
        directory = '/' + directory

    # Verify filename and format it.
    if filename.startswith('.'):
        filename = filename[1:]
    if filename.startswith('/'):
        filename = filename[1:]

    return '{directory}{filename}'.format(
        directory=directory, filename=filename)


def on_message(channel, method, properties, body):
    """
    Invokes the relevant video chunking method based
    on the message.
    """
    # Convert to dictionary.
    message = ''

    try:
        message = json.loads(body)
        # Act on the message.
        filename = message['ParentFile'] if 'ParentFile' in message.keys(
        ) else None
        start_frame = message['StartFrame'] if 'StartFrame' in message.keys(
        ) else None
        end_frame = message['EndFrame'] if 'EndFrame' in message.keys(
        ) else None

        video_path = absolute_path(VIDEO_DIRECTORY, filename)

        print(
            '[PROCESSING] Worker:{worker} --> Video:{video} --> Start Frame:{start_frame} <--> End Frame:{end_frame}'
            .format(
                worker=str(WORKER_ID),
                video=video_path,
                start_frame=str(start_frame),
                end_frame=str(end_frame)))

        # Process the chunk.
        head_c,code_c,slide_c  = videoStyles(video_path, start_frame, end_frame)
        classification = {'Talking Head': head_c, 'Slides': slide_c, 'Code': code_c}
        # Send the response.
        # This response should have all the info of the initial message.
        # NOTE: Responses are sent to a different queue.
        response = message
        response['Classification'] = classification
        response['WorkerId'] = str(WORKER_ID)
        ANALYZER_QUEUE.basic_publish(
            exchange='',
            routing_key=ANALYZER_KEY,
            body=json.dumps(response, default=str))

        # Send acknowladgement.
        channel.basic_ack(delivery_tag=method.delivery_tag)

        print(
            '[CLASSIFIED] Worker:{worker} --> Video:{video} --> Start Frame:{start_frame} <--> End Frame:{end_frame} --> Classification:{classification}'
            .format(
                worker=str(WORKER_ID),
                video=video_path,
                start_frame=str(start_frame),
                end_frame=str(end_frame),
                classification=classification))

    except ValueError:
        message = body

# Init connection.
# MQ details.
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
