FROM python:3.12-slim

WORKDIR /app
ARG BACKEND_HOST=0.0.0.0
ARG BACKEND_PORT=8000
ENV BACKEND_HOST=${BACKEND_HOST}
ENV BACKEND_PORT=${BACKEND_PORT}

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE ${BACKEND_PORT}

CMD ["sh", "-c", "uvicorn github_compliance_engine_api.main:create_app --factory --host ${BACKEND_HOST} --port ${BACKEND_PORT}"]
