FROM python:3.12-slim

WORKDIR /usr/src/app

# Copy requirements first so this layer is cached separately from source code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./webservice.py"]
