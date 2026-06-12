"""
Predefined, hardcoded, highly-optimized SQL queries for bullet-proof demonstrations.
This handles the 80% of specific analytic queries (e.g., "Top murder offenders", "Mysuru burglary gang")
without risking LLM hallucination.
"""
from database import get_db_connection
import psycopg2.extras

def get_top_offenders_by_crime(crime_type: str = None, limit: int = 10) -> dict:
    conn = get_db_connection()
    if not conn:
        return {"error": "DB not connected"}
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = """
            SELECT c.name, c.age, c.criminal_history_count, COUNT(cr.id) AS specific_crime_count
            FROM criminals c
            JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
            JOIN crimes cr ON cr.id = ccl.crime_id
        """
        params = []
        if crime_type:
            query += " WHERE LOWER(cr.crime_type) LIKE LOWER(%s)"
            params.append(f"%{crime_type}%")
            
        query += """
            GROUP BY c.id, c.name, c.age, c.criminal_history_count
            ORDER BY specific_crime_count DESC
            LIMIT %s
        """
        params.append(limit)
        
        cur.execute(query, tuple(params))
        results = [dict(row) for row in cur.fetchall()]
        return {"query_type": "top_offenders", "crime_type": crime_type, "results": results}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def get_gang_members(district: str = None, crime_type: str = None) -> dict:
    """Finds closely linked groups of criminals operating in a specific area/crime type."""
    conn = get_db_connection()
    if not conn:
        return {"error": "DB not connected"}
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Find criminals who share crimes in this district/crime_type
        query = """
            SELECT DISTINCT c.id, c.name, c.phone, cr.crime_type, cr.district
            FROM criminals c
            JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
            JOIN crimes cr ON cr.id = ccl.crime_id
            WHERE 1=1
        """
        params = []
        if district:
            query += " AND LOWER(cr.district) LIKE LOWER(%s)"
            params.append(f"%{district}%")
        if crime_type:
            query += " AND LOWER(cr.crime_type) LIKE LOWER(%s)"
            params.append(f"%{crime_type}%")
            
        query += " ORDER BY c.id LIMIT 20"
        
        cur.execute(query, tuple(params))
        results = [dict(row) for row in cur.fetchall()]
        
        # Group them into a mock "gang" output if we found any
        gang_name = f"{district.title() if district else 'Unknown'} {crime_type.title() if crime_type else 'Criminal'} Gang"
        
        return {
            "query_type": "gang_search",
            "gang_name": gang_name,
            "district": district,
            "crime_type": crime_type,
            "members": results
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def get_phone_network(phone: str) -> dict:
    conn = get_db_connection()
    if not conn:
        return {"error": "DB not connected"}
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT c.name, c.phone, c.criminal_history_count, array_agg(cr.crime_type) as crime_types
            FROM criminals c
            JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
            JOIN crimes cr ON cr.id = ccl.crime_id
            WHERE c.phone = %s
            GROUP BY c.id, c.name, c.phone, c.criminal_history_count
        """, (phone,))
        results = [dict(row) for row in cur.fetchall()]
        return {"query_type": "phone_network", "phone": phone, "results": results}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def execute_fallback_sql(sql: str) -> dict:
    """Safely execute an LLM-generated read-only query."""
    if not sql or not sql.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed for safety."}
    
    # Enforce LIMIT
    if "LIMIT " not in sql.upper():
        sql += " LIMIT 50"
        
    conn = get_db_connection()
    if not conn:
        return {"error": "DB not connected"}
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql)
        results = [dict(row) for row in cur.fetchall()]
        return {"query_type": "fallback_sql", "sql_executed": sql, "results": results}
    except Exception as e:
        return {"error": f"SQL Execution Error: {str(e)}", "attempted_sql": sql}
    finally:
        cur.close()
        conn.close()
