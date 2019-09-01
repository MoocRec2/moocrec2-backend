"""
Contains commonly used functions related to RabbitMQ.
"""

from datetime import datetime
import sys
import pika

def init_mq(host='localhost', port=5672, username='guest', password='guest', name_queue='default_queue'):
    """ 
    Establish a connection to RabbitMQ and return the,
    communication channel.

    :param host
        Hostname/ip at which RabbitMQ is available/listening.
        DEFAULT: localhost
    :param name_queue
        Name of the message queue.
        DEFAULT: default_queue
    :returns channel
        A channel with our queue created in it.
    """

    print ('Attempting connection to RabbitMQ on {host}:{port} and queue:{queue} as user:{user}'.format(host=host, port=port, queue=name_queue, user=username))

    # Set up credentials.
    credentials = pika.PlainCredentials(username, password)
    # Set up parameters for connection.
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    # Set up connection and queue.
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=name_queue)
    
    return channel
