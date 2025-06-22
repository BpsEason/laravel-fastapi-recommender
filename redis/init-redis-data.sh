#!/bin/bash
REDIS_HOST="localhost"
REDIS_PORT="6379"

echo "Connecting to Redis at ${REDIS_HOST}:${REDIS_PORT}..."

/usr/bin/redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping
while [ $? -ne 0 ]; do
    echo "Waiting for Redis to start..."
    sleep 1
    /usr/bin/redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping
done

echo "Redis is up and running. Initializing data..."

/usr/bin/redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" SET "user:1:recommendations" "[101, 102, 103]" EX 3600
echo "Set initial recommendations for user 1."

echo "Redis data initialization complete."
