FROM python:alpine3.6

RUN mkdir -p /app

COPY * /app/

RUN pip3 --no-cache-dir install -r /app/requirements.txt

WORKDIR /app

CMD ["python3", "-u", "/app/potd.py", "schedule"]
