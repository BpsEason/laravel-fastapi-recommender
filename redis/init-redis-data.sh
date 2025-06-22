#!/bin/bash
REDIS_HOST="localhost"
REDIS_PORT="6379"

echo "Connecting to Redis at ${REDIS_HOST}:${REDIS_PORT}..."

# Loop until Redis is reachable
until /usr/bin/redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping; do
    echo "Waiting for Redis to start..."
    sleep 1
done

echo "Redis is up and running. Initializing data..."

# Set initial recommendations for user 1 with a TTL
/usr/bin/redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" SET "user:1:recommendations" "[101, 102, 103]" EX 3600
echo "Set initial recommendations for user 1 with TTL."

echo "Redis data initialization complete."
