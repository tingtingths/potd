FROM python:3.8-slim-buster as builder

RUN mkdir -p /app

COPY * /app/

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install --target=/install -r /app/requirements.txt

FROM python:3.8-alpine3.12

RUN apk add tzdata

COPY --from=builder /install /usr/local/lib/python3.8/site-packages

COPY * /app/

WORKDIR /app

CMD ["python3", "-u", "/app/potd.py"]
