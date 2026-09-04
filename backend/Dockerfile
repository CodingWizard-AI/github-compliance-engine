FROM python:3.12-slim

WORKDIR /app
ARG BACKEND_HOST=0.0.0.0
ARG BACKEND_PORT=8000
ARG GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git
ENV BACKEND_HOST=${BACKEND_HOST}
ENV BACKEND_PORT=${BACKEND_PORT}
ENV GIT_PYTHON_GIT_EXECUTABLE=${GIT_PYTHON_GIT_EXECUTABLE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE ${BACKEND_PORT}

CMD ["sh", "-c", "uvicorn github_compliance_engine_api.main:create_app --factory --host ${BACKEND_HOST} --port ${BACKEND_PORT}"]
