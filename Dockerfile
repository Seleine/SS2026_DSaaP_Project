FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY config.py .
COPY src/ src/

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "src/analysis.py"]
CMD []