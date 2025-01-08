FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
COPY . .
RUN uv sync
EXPOSE 5006
CMD ["uv", "run", "--group", "webapp", "panel", "serve", "webapp/app.py"]
