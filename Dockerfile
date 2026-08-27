FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SPARK_LOCAL_IP=127.0.0.1 \
    PYSPARK_PYTHON=python3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data/raw /app/data/processed /app/data/reports

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["sh", "-c", "python main.py && streamlit run src/dashboard/app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true"]
