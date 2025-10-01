FROM python:3.10.18-slim-bookworm

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./FitBridge.py"]
