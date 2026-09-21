FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt
COPY app.py .
COPY static/ static/
COPY templates/ templates/
ENV HOST=0.0.0.0
CMD ["python", "app.py"]
