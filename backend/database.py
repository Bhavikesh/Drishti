import os
import psycopg2

SUPABASE_URL = os.getenv("SUPABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

def get_db_connection():
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
