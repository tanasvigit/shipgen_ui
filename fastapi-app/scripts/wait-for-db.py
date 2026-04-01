#!/usr/bin/env python3
"""
Wait for database to be ready and create it if it doesn't exist.
"""
import sys
import time
import psycopg2
from psycopg2 import OperationalError, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database_if_not_exists(host, port, database, user, password):
    """Create database if it doesn't exist."""
    try:
        # Connect to postgres database to create the target database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database='postgres',  # Connect to default postgres database
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Database '{database}' does not exist. Creating it...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(database)
                )
            )
            print(f"Database '{database}' created successfully!")
        else:
            print(f"Database '{database}' already exists.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def wait_for_db(host, port, database, user, password, max_retries=30, delay=2):
    """Wait for database to be ready and create it if needed."""
    print(f"Waiting for PostgreSQL server at {host}:{port}...")
    
    # First, wait for PostgreSQL server to be available
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database='postgres',  # Try connecting to default database first
                user=user,
                password=password,
                connect_timeout=2
            )
            conn.close()
            print("PostgreSQL server is ready!")
            break
        except OperationalError:
            if i < max_retries - 1:
                print(f"PostgreSQL server not ready, waiting {delay} seconds... ({i+1}/{max_retries})")
                time.sleep(delay)
            else:
                print("PostgreSQL server connection failed after maximum retries")
                return False
    
    # Create database if it doesn't exist
    if not create_database_if_not_exists(host, port, database, user, password):
        return False
    
    # Now wait for the target database to be ready
    print(f"Waiting for database '{database}' to be ready...")
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            conn.close()
            print(f"Database '{database}' is ready!")
            return True
        except OperationalError:
            if i < max_retries - 1:
                print(f"Database '{database}' not ready, waiting {delay} seconds... ({i+1}/{max_retries})")
                time.sleep(delay)
            else:
                print(f"Database '{database}' connection failed after maximum retries")
                return False
    
    return False

if __name__ == "__main__":
    import os
    
    host = os.getenv("DB_HOST", "db")
    port = int(os.getenv("DB_PORT", "5432"))
    database = os.getenv("DB_DATABASE", "techliv")
    user = os.getenv("DB_USERNAME", "techliv")
    password = os.getenv("DB_PASSWORD", "techliv")
    
    if not wait_for_db(host, port, database, user, password):
        sys.exit(1)

