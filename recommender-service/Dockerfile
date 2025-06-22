FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies for building scipy/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libblas-dev \
    liblapack-dev \
    gfortran \
    # For MySQL client library
    libmysqlclient-dev \
    default-mysql-client \
    # Clean up APT cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

COPY recommender-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY recommender-service/app ./app
COPY recommender-service/tests ./tests # Copy tests for CI/CD

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application - will be overridden by docker-compose for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
