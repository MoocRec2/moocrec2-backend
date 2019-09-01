"""
This is responsible for analyzing each message in analyzer_queue,
and construct a final classification/conclusion by analyzing the,
classifications given to each video chunk of a specific video file.

To avoid having to wait till all the chunks of a video file are classified,
in order to give the final classification, this will update the classification
in the DB as the outputs arrive.
"""

from datetime import datetime
from database import document_exists, save, get_one
from mq_common import init_mq
from time import time
import random
import json
import os
import sys
import subprocess


def on_message(channel, method, properties, body):
    # Convert to dictionary.
    message = ''

    try:
        message = json.loads(body)
        # Act on the message.
        mooc = message['ParentMooc'] if 'ParentMooc' in message.keys(
        ) else None
        position = message['Position'] if 'Position' in message.keys(
        ) else None
        total = message['Total'] if 'Total' in message.keys(
        ) else None
        classifications = message['Classification'] if 'Classification' in message.keys(
        ) else None

        print(message, classifications, mooc)
        if classifications is not None and mooc is not None:

            probability_talking_head = classifications['Talking Head']
            probability_slides = classifications['Slides']
            probability_code = classifications['Code']
            
            if not document_exists('moocrec-v2', 'classifications', 'Course', mooc):
                new_document = {
                    'TalkingHead': probability_talking_head,
                    'Slides': probability_slides,
                    'Code': probability_code,
                    'Course': mooc
                }
                save('moocrec-v2', 'classifications', 'Course', mooc, new_document)
            else:
                # Update the existing classifications.
                existing_document = get_one('moocrec-v2', 'classifications', 'Course', mooc)
                updated_document = {
                    'TalkingHead': (existing_document['TalkingHead'] + probability_talking_head) / 2,
                    'Slides': (existing_document['Slides'] + probability_slides) / 2,
                    'Code': (existing_document['Code'] + probability_code) / 2
                }
                save('moocrec-v2', 'classifications', 'Course', mooc, updated_document)

        # Send acknowladgement.
        channel.basic_ack(delivery_tag=method.delivery_tag)

        #print(
        #    '[CLASSIFIED] Worker:{worker} --> Video:{video} --> Start Frame:{start_frame} <--> End Frame:{end_frame} --> Classification:{classification}'
        #    .format(
        #        worker=str('WORKER_ID'),
        #        video='video_path',
        #        start_frame=str(start_frame),
        #        end_frame=str(end_frame),
        #        classification='classification'))

    except ValueError:
        message = body

# Init connection.
# MQ details.
ANALYZER_KEY = os.getenv('MQ_ANALYZER_QUEUE_NAME', 'analyzer_queue')
HOST = os.getenv('MQ_HOST', '13.127.220.123')
USERNAME = os.getenv('MQ_USERNAME', 'analyzer')
PASSWORD = os.getenv('MQ_PASSWORD', 'analyzer')
VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY', '/tmp')

ANALYZER_QUEUE = init_mq(
    host=HOST, name_queue=ANALYZER_KEY, username=USERNAME, password=PASSWORD)

# Prep for consuming.
print('[SUCCESS] Output analyzer started') 
# We only acknowladge the message after the task is complete,
# This ensures that the message remains in the qeueu even if the,
# worker crashes during processing.
ANALYZER_QUEUE.basic_consume(
    queue=ANALYZER_KEY, auto_ack=False, on_message_callback=on_message)
# Start.
ANALYZER_QUEUE.start_consuming()