# Containerized video classifier.
# External pip modules are needed to run the MQ connection,
# and the classifier.
# Therefore, an intermediate container is used to first install,
# those modules via requirements.txt
FROM jjanzic/docker-python3-opencv

WORKDIR /app

# Install Python3.7 and other libraries(pika lib).
RUN pip3 install pika keras tensorflow pillow

COPY mq_common.py /app
COPY worker.py /app
COPY classifier.py /app
COPY vgg16_model.h5 /app
#COPY ./video_classifier /usr/src/app/video-classifier
#ADD video-classifier /usr/src/app
#RUN mkdir -p /usr/src/app/video-classifier/images

CMD ["python3", "./worker.py"]