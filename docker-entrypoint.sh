#!/bin/bash
set -e

echo "🚀 Starting SAPDOCAI Application..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python -c "
import time
import mysql.connector
import psycopg2
from database_manager import db_manager

# Wait for MySQL
mysql_ready = False
for i in range(30):
    try:
        with db_manager.get_mysql_connection() as conn:
            mysql_ready = True
            print('✅ MySQL is ready!')
            break
    except:
        print(f'⏳ Waiting for MySQL... ({i+1}/30)')
        time.sleep(2)

# Wait for PostgreSQL
postgres_ready = False
for i in range(30):
    try:
        with db_manager.get_postgres_connection() as conn:
            postgres_ready = True
            print('✅ PostgreSQL is ready!')
            break
    except:
        print(f'⏳ Waiting for PostgreSQL... ({i+1}/30)')
        time.sleep(2)

if not mysql_ready:
    print('❌ MySQL failed to start')
    exit(1)

if not postgres_ready:
    print('❌ PostgreSQL failed to start')
    exit(1)
"

# Run database migrations if needed
echo "📊 Running database migrations..."
python -c "
from database_manager import db_manager
print('✅ Database migrations completed')
"

# Start the application
echo "🎯 Starting Streamlit application..."
exec "$@"
