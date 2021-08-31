FROM python:2-alpine

COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache --virtual .deps libffi \
&& apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev \
&& pip install -r /tmp/requirements.txt \
&& apk del .build-deps \
&& rm -rf /root/.cache/pip
