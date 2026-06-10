import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

async def log_audit(user_id: int, query: str, response: str, ip_address: str, session_id: str = None):
    if not supabase:
        print(f"Audit Log (mock): user={user_id}, query='{query}'")
        return
        
    try:
        data = {
            "user_id": user_id,
            "query": query,
            "response": response,
            "ip_address": ip_address
        }
        # In a real app, you might want to add session_id to the audit_logs table schema
        supabase.table("audit_logs").insert(data).execute()
    except Exception as e:
        print(f"Error logging audit: {e}")

def search_audit_logs(user_id=None, start_date=None, end_date=None):
    if not supabase:
        return []
    
    query = supabase.table("audit_logs").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    # Add date filters if needed
    
    response = query.execute()
    return response.data
