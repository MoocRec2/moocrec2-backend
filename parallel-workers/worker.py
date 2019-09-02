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
import pika
import subprocess

# MQ details.
WORKER_KEY = os.getenv('MQ_WORKER_QUEUE_NAME', 'worker_queue')
ANALYZER_KEY = os.getenv('MQ_ANALYZER_QUEUE_NAME', 'analyzer_queue')
HOST = os.getenv('MQ_HOST', '13.127.220.123')
USERNAME = os.getenv('MQ_USERNAME', 'worker')
PASSWORD = os.getenv('MQ_PASSWORD', 'worker')
VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY', '/tmp')

WORKER_ID = None

WORKER_QUEUE = None 
ANALYZER_QUEUE = None


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
        head_p,code_p,slide_p,animation_p,writing_p  = videoStyles(video_path, start_frame, end_frame)
        classification = {'Talking Head': head_p, 'Slides': slide_p, 'Code': code_p, 'Animation': animation_p, 'Writing': writing_p}
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

def main():
    global WORKER_KEY, ANALYZER_KEY, HOST, USERNAME, PASSWORD, VIDEO_DIRECTORY, WORKER_ID, WORKER_QUEUE, ANALYZER_QUEUE

    while (True):   
        try:
            # Set up credentials.
            credentials = pika.PlainCredentials(USERNAME, PASSWORD)
            # Set up parameters for connection.
            parameters = pika.ConnectionParameters(HOST, 5672, '/', credentials)
            # Set up connection.
            connection = pika.BlockingConnection(parameters)
            # Queues.
            WORKER_QUEUE = connection.channel()
            WORKER_QUEUE.queue_declare(queue=WORKER_KEY)
            ANALYZER_QUEUE = connection.channel()
            ANALYZER_QUEUE.queue_declare(queue=ANALYZER_KEY)
            # Get a random worker_id. If this is running on Docker, container id will be random.
            hostname = get_hostname()
            WORKER_ID = hostname['Output'] if hostname['Successful'] else str(int(time())) + str(random.randint(0, 9))

            # Prep for consuming.
            print('Worker', WORKER_ID, 'started.\n\n')

            # Listen forever.
            try:
                # We only acknowladge the message after the task is complete,
                # This ensures that the message remains in the qeueu even if the,
                # worker crashes during processing.
                WORKER_QUEUE.basic_consume(
                    queue=WORKER_KEY, auto_ack=False, on_message_callback=on_message)
                WORKER_QUEUE.start_consuming()
            except KeyboardInterrupt:
                WORKER_QUEUE.stop_consuming()
                connection.close()
                break
        
        # If heartbeat fails when the on_message takes long to return.
        except pika.exceptions.ConnectionClosedByBroker:
            continue # continue the loop and re-establish the connection.
        except pika.exceptions.AMQPHeartbeatTimeout:
            continue
        except pika.exceptions.StreamLostError:
            continue

if __name__ == "__main__":
    main()