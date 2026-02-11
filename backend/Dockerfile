FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY . .

RUN chmod +x /app/entrypoint.sh /app/scripts/run_migrations.sh
RUN mkdir -p /var/log/kasperjunge

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
