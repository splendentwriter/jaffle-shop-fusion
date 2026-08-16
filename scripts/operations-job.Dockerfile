FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY generate_operations_data.py .

ENTRYPOINT ["python3", "generate_operations_data.py"]
