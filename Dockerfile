FROM python:alpine3.6

RUN mkdir -p /app

COPY *.py /app/
COPY requirements.txt /app

RUN pip3 --no-cache-dir install -r /app/requirements.txt

CMD ["python3", "-u", "/app/potd.py", "schedule"]
