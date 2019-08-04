# Containerized video classifier.
# External pip modules are needed to run the MQ connection,
# and the classifier.
# Therefore, an intermediate container is used to first install,
# those modules via requirements.txt
FROM python:3.7-slim

WORKDIR /usr/src/app

# Install Python3.7 and other libraries(pika lib).
RUN pip install pika opencv-python 

COPY mq_common.py /usr/src/app
COPY worker.py /usr/src/app
#ADD video-classifier /usr/src/app
#RUN mkdir -p /usr/src/app/video-classifier/images

CMD ["python", "./worker.py"]