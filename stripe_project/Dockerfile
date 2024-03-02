FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod a+x /app/run.sh

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stripe_project.wsgi"] 
