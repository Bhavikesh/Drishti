from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import langgraph_router
import translation
from utils import session_manager, audit_logger

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    language: str = "en"

@router.post("/")
async def chat_endpoint(request: Request, body: ChatRequest):
    user_id = getattr(request.state, "user", {}).get("id", 0)
    ip_address = request.client.host
    
    # 1. Translate to English if needed
    english_query = translation.translate_to_english(body.message)
    
    # 2. Add to session
    session_manager.add_message(body.session_id, "user", english_query)
    context = session_manager.get_context(body.session_id)
    
    # 3. Route through LangGraph multi-agent system
    try:
        result = langgraph_router.route_query(english_query, context)
        ai_response = result.get("response", "I couldn't process your request.")
    except Exception as e:
        import traceback
        print(f"LangGraph error: {e}")
        traceback.print_exc()
        ai_response = "I'm sorry, I couldn't process your request at this time."
        result = {"sources": [], "confidence": 0.5, "agent": "ERROR"}
        
    session_manager.add_message(body.session_id, "assistant", ai_response)
    
    # 4. Translate back if needed
    if body.language.startswith("kn") or translation.detect_language(body.message) == "kn":
        final_response = translation.translate_to_kannada(ai_response)
    else:
        final_response = ai_response
        
    # 5. Audit Logging
    await audit_logger.log_audit(user_id, body.message, final_response, ip_address, body.session_id)
    
    return {
        "response": final_response,
        "sources": result.get("sources", []),
        "confidence": result.get("confidence", 0.85),
        "agent": result.get("agent", "DATABASE"),
        "stats": result.get("stats", None),
        "network_data": result.get("network_data", None),
        "prediction_data": result.get("prediction_data", None),
        "sql_results": result.get("sql_results", None),
        "investigate_query": english_query, # Suggest this for the detective board
    }
