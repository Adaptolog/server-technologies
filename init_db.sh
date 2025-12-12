#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Initialize migrations if they don't exist
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
fi

# Create migrations and upgrade database
echo "Creating database migrations..."
flask db migrate -m "Initial migration"

echo "Upgrading database..."
flask db upgrade

echo "Database initialized successfully!"