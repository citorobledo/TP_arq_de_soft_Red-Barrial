FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv

COPY requirements.txt .
COPY wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY src/ ./
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && useradd --uid 1000 --create-home app \
    && mkdir /data && chown app:app /data

USER app
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
