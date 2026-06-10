from typing import List, Dict

# In-memory session storage: { session_id: [{"role": "user"/"assistant", "content": "..."}] }
sessions: Dict[str, List[Dict[str, str]]] = {}

def add_message(session_id: str, role: str, content: str):
    if session_id not in sessions:
        sessions[session_id] = []
    
    sessions[session_id].append({"role": role, "content": content})
    
    # Keep max 10 exchanges (20 messages)
    if len(sessions[session_id]) > 20:
        sessions[session_id] = sessions[session_id][-20:]

def get_context(session_id: str) -> List[Dict[str, str]]:
    return sessions.get(session_id, [])

def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
