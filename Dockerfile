FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY src/config.py .
COPY src/ src/
COPY tests/ tests/
COPY data_tractive/ data_tractive/

#RUN pip install --no-cache-dir .[dev]
RUN pip install --no-cache-dir . \
    && pip install pytest pytest-cov coverage ruff

ENTRYPOINT ["python", "src/main.py"]
CMD []