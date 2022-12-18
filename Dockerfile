FROM python:3.9-alpine3.13
WORKDIR /app
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
ENV PYTHONUNBUFFERED 1
EXPOSE 8000
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
      then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi &&\
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        user

ENV PATH="/py/bin:$PATH"
USER user

