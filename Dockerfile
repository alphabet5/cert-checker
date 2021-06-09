FROM python:3-alpine as builder

RUN find / -iname wheelhouse
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo
RUN apk add --no-cache libressl-dev musl-dev curl bash perl
RUN mkdir /out
COPY ./build.sh ./build.sh
RUN pip install virtualenv
RUN ./build.sh

CMD [ "sh" ]

FROM python:3-alpine
LABEL maintainer="John Burt"

ENV NOTIFICATION_TIME=7d

WORKDIR /usr/src/app

RUN mkdir /installs
COPY --from=builder /cffi-*.whl /whl/
COPY --from=builder /cryptography-*.whl /whl/
COPY --from=builder /pycparser-*.whl /whl/
COPY --from=builder /openssl-*.whl /whl/

RUN pip install /whl/*
RUN pip install --no-cache-dir pyopenssl schedule
RUN rm -rf /whl

COPY cert_checker.py ./

CMD [ "python", "./cert_checker.py" ]