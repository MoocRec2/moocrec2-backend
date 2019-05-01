# Containerized video classifier.
# External pip modules are needed to run the MQ connection,
# and the classifier.
# Therefore, an intermediate container is used to first install,
# those modules via requirements.txt
FROM alpine:3.7

# Install Python3.7 and other libraries(pika lib).
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache && \
    pip3 install pika

COPY mq_common.py /
COPY worker.py /

CMD ["python3", "/worker.py"]