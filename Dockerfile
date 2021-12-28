FROM python:3.9-alpine
LABEL maintainer="alphabet5"

ENV NOTIFICATION_TIME=7d
ENV LOG_LOCALS=False

WORKDIR /usr/src/app

RUN pip install --no-cache-dir rich 

COPY cert_checker.py ./

CMD [ "python", "./cert_checker.py" ]