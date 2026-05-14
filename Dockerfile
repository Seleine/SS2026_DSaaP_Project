FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY config.py .
COPY src/ src/

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "src/analysis.py"]
CMD []