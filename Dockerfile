FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
COPY . .
RUN uv sync
EXPOSE 80
CMD ["uv", "run", "--group", "webapp", "panel", "serve", "--port", "80", "webapp/app.py"]
