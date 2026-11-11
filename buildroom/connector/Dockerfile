# Build Room connector image. Build from the repository root:
#   docker build -f buildroom/connector/Dockerfile .
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BUILDROOM_USAGE_LOG=stdout
WORKDIR /app
COPY buildroom/connector/server.py buildroom/connector/members.py buildroom/connector/join.py /app/buildroom/connector/
COPY buildroom/skills /app/buildroom/skills
COPY buildroom/rollout/releases/README.md /app/buildroom/rollout/releases/README.md
RUN useradd --create-home --uid 10001 connector && chown -R connector /app
USER connector
CMD ["sh", "-c", "python3 buildroom/connector/server.py --host 0.0.0.0 --port ${PORT:-8787}"]
