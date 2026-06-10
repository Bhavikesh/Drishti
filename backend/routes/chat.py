from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import mistral_client
import rag_pipeline
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
    
    # 3. RAG Retrieval
    try:
        rag_results = rag_pipeline.retrieve_relevant_crimes(english_query)
        # Format sources from rag_results for mistral
        sources_text = "\n".join([doc for doclist in rag_results['documents'] for doc in doclist]) if rag_results and 'documents' in rag_results else ""
    except Exception as e:
        sources_text = ""
        rag_results = []
        
    # 4. Query Mistral
    prompt = f"Context: {sources_text}\n\nChat History: {context}\n\nUser Query: {english_query}"
    system_prompt = "You are Drishti, an AI assistant for Karnataka State Police. Answer crime-related queries using only provided data. Be concise and professional."
    
    try:
        mistral_response = mistral_client.query_mistral(prompt, system_prompt)
    except Exception as e:
        mistral_response = "I'm sorry, I couldn't process your request at this time."
        
    session_manager.add_message(body.session_id, "assistant", mistral_response)
    
    # 5. Translate back if needed
    if body.language.startswith("kn") or translation.detect_language(body.message) == "kn":
        final_response = translation.translate_to_kannada(mistral_response)
    else:
        final_response = mistral_response
        
    # 6. Audit Logging
    await audit_logger.log_audit(user_id, body.message, final_response, ip_address, body.session_id)
    
    return {
        "response": final_response,
        "sources": rag_results.get('metadatas', []) if isinstance(rag_results, dict) else [],
        "confidence": 0.95  # Mock confidence
    }
