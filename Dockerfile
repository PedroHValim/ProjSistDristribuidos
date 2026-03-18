FROM python:3.13.12-slim-trixie

WORKDIR /app

RUN pip install pyzmq

CMD ["python", "main.py"]