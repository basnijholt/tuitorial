FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
RUN addgroup --system appgroup && \
    adduser --system --group --home /home/appuser appuser
COPY --chown=appuser:appgroup . /app
WORKDIR /app
USER appuser
RUN uv sync
EXPOSE 80
CMD ["uv", "run", "--group", "webapp", "panel", "serve", "--port", "7860", "--address", "0.0.0.0", "--allow-websocket-origin", "*", "webapp/app.py"]
