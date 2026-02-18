FROM postgres:15-alpine

# Set default environment variables (overridable via docker-compose or env)
ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=app_db

# Optional: initialize scripts can be placed in infra/docker/postgres-init.d
# and will be executed on first container startup
COPY postgres-init.d/ /docker-entrypoint-initdb.d/

# Expose default Postgres port
EXPOSE 5432

# Use the default entrypoint provided by the Postgres image