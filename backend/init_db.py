import psycopg2
from database import get_db_connection

def init_database():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database. Cannot initialize.")
        return
        
    cur = conn.cursor()
    
    # 1. Database Schema
    schema = """
    -- Enable PostGIS for geospatial queries
    CREATE EXTENSION IF NOT EXISTS postgis;

    CREATE TABLE IF NOT EXISTS police_stations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        district VARCHAR(50),
        jurisdiction_area TEXT,
        lat FLOAT,
        lng FLOAT,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS crimes (
        id SERIAL PRIMARY KEY,
        case_id VARCHAR(20) UNIQUE,
        crime_date DATE,
        district VARCHAR(50),
        police_station_id INTEGER REFERENCES police_stations(id),
        crime_type VARCHAR(50),
        description TEXT,
        status VARCHAR(30),
        lat FLOAT,
        lng FLOAT,
        is_resolved BOOLEAN,
        resolution_date DATE
    );

    CREATE TABLE IF NOT EXISTS criminals (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INTEGER,
        gender VARCHAR(10),
        criminal_history_count INTEGER DEFAULT 0,
        is_repeat_offender BOOLEAN,
        first_offense_date DATE
    );

    CREATE TABLE IF NOT EXISTS crime_criminal_links (
        id SERIAL PRIMARY KEY,
        crime_id INTEGER REFERENCES crimes(id),
        criminal_id INTEGER REFERENCES criminals(id),
        role VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(100) UNIQUE,
        password_hash VARCHAR(255),
        role VARCHAR(20),
        assigned_district VARCHAR(50),
        assigned_station_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        query TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT NOW(),
        ip_address VARCHAR(50)
    );
    """
    
    try:
        cur.execute(schema)
        
        # 2. Insert default admin
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin_hash = pwd_context.hash("Admin@123")
        
        cur.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING",
            ("admin@ksp.gov.in", admin_hash, "admin")
        )
        
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()
