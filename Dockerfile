FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#ENV OUTPUT_DIR=/app/plots
#ENV IN_DOCKER=1


WORKDIR /app

COPY pyproject.toml .
COPY src/config.py .
COPY src/ src/
COPY data_tractive/ data_tractive/

RUN pip install --no-cache-dir .[dev]

ENTRYPOINT ["python", "src/main.py"]
CMD []