# Build stage with Node.js for NX and Python for Poetry
FROM pfeiffermax/python-poetry:1.15.0-poetry1.8.5-python3.12.9-slim-bookworm AS nx-builder

# Set environment variables
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR="/app/.cache/pypoetry" \
    PYTHONPATH=/app

# Install Node.js for NX
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Set up work directory
WORKDIR /app

# Copy configuration files for NX
COPY package.json package-lock.json* nx.json ./

# Install NX and its dependencies
RUN npm install

# Copy the rest of the project files
COPY . .

# Install Python dependencies using NX (which uses Poetry)
RUN npx nx install users

# Optional: Debug to verify that the virtual environment exists
RUN ls -la /app/packages/services/users && \
    find /app/packages/services/users -name ".venv" -type d

# Production stage
FROM python:3.12.0-slim as production-image

ARG APPLICATION_SERVER_PORT=8000

# Set environment variables and define the virtual environment path
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    VIRTUAL_ENVIRONMENT_PATH="/app/packages/services/users/.venv" \
    APPLICATION_SERVER_PORT=$APPLICATION_SERVER_PORT

# Add the virtual environment to PATH to "activate" it
ENV PATH="$VIRTUAL_ENVIRONMENT_PATH/bin:$PATH"

# Create a non-root user
RUN groupadd -g 10001 python_application && \
    useradd -r -u 10001 -g python_application python_application

WORKDIR /app

# Copy the application code from the builder stage
COPY --from=nx-builder /app/packages /app/packages

# Copy the virtual environment from the builder stage
COPY --from=nx-builder /app/packages/services/users/.venv $VIRTUAL_ENVIRONMENT_PATH

# Install PostgreSQL client tools, tzdata, and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata postgresql-client curl && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create the entrypoint script
RUN echo '#!/bin/bash\n\
# Wait for PostgreSQL to be ready\n\
echo "Waiting for PostgreSQL at $DATABASE_HOST:$DATABASE_PORT..."\n\
until PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT 1" > /dev/null 2>&1; do\n\
  echo "PostgreSQL not ready yet - sleeping for 1 second"\n\
  sleep 1\n\
done\n\
echo "PostgreSQL is ready!"\n\
\n\
# Set PYTHONPATH to include all necessary packages\n\
export PYTHONPATH=$PYTHONPATH:/app/packages/services/users:/app/packages/libs/api:/app/packages/libs/auth:/app/packages/libs/db:/app/packages/libs/shared-models\n\
\n\
# Start the application using the virtual environment\'s Python\n\
cd /app/packages/services/users\n\
python -m booking_users.main\n' > /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Set ownership of application files and entrypoint script
RUN chown -R python_application:python_application /app /entrypoint.sh

# Switch to non-root user
USER python_application

# Expose the application port
EXPOSE ${APPLICATION_SERVER_PORT}

ENTRYPOINT ["/entrypoint.sh"]
