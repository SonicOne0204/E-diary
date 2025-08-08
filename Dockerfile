FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
PYTHONDONTWRITEBYTECODE=1 

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
 
EXPOSE 5000

ENTRYPOINT [ "uvicorn"]
CMD [ "app.main:app", "--host", "0.0.0.0", "--port", "5000" ]

