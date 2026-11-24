# Build Room connector image. Build from the repository root:
#   docker build -f buildroom/connector/Dockerfile .
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BUILDROOM_USAGE_LOG=stdout
WORKDIR /app
COPY buildroom/connector/server.py buildroom/connector/members.py buildroom/connector/join.py buildroom/connector/usage.py buildroom/connector/billing.py buildroom/connector/dashboard.html buildroom/connector/guide.html buildroom/connector/start.html buildroom/connector/example-review.html buildroom/connector/example-build.html buildroom/connector/example-onepage.html buildroom/connector/example-offer-page.html buildroom/connector/example-sales-script.html buildroom/connector/example-referrals.html /app/buildroom/connector/
COPY buildroom/skills /app/buildroom/skills
COPY buildroom/rollout/releases/README.md /app/buildroom/rollout/releases/README.md
RUN useradd --create-home --uid 10001 connector && chown -R connector /app
USER connector
CMD ["sh", "-c", "python3 buildroom/connector/server.py --host 0.0.0.0 --port ${PORT:-8787}"]
