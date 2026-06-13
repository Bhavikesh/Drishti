"""
AI Client for CrimeMind AI (Switched to Groq for Hackathon Speed & Reliability)
We keep the filename 'gemini_client.py' to avoid breaking imports elsewhere.
"""
import os
import json
import traceback
import requests
from pathlib import Path
from dotenv import load_dotenv

# Always load .env from the same directory as this file
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    print(f"✅ Groq client initialized (key ends with ...{GROQ_API_KEY[-6:]})")
else:
    print("⚠️ GROQ_API_KEY not set!")

SYSTEM_PROMPT = """You are a Crime Intelligence Officer. You are NOT a generic AI assistant. You DO NOT write essays, introductions, or generic explanations.

Every answer MUST strictly follow this exact 4-part structure:

1. Direct Answer
Provide the immediate answer to the query (e.g., top offenders, hotspots).
2. Evidence
List the supporting data from the database (e.g., Linked Cases, Connected Suspects).
3. Analysis
Provide one key insight (e.g., Network Influence, Confidence Score).
4. Recommendation
Give one specific tactical recommendation for law enforcement.

DO NOT use conversational filler like "Here is the information you requested" or "Crime is a serious issue".
DO NOT hallucinate data. If the data is not in the provided SQL results or RAG context, say "Insufficient data in intelligence database."
Always format with clear headings and bullet points."""

def _call_groq(prompt: str, system_prompt: str = None, json_mode: bool = False, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=1500) -> str:
    """Wrapper to call Groq's REST API natively to avoid sandbox/dependency issues"""
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
        
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Groq API returned {response.status_code}: {response.text}")
            
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"🔴 Groq API error: {str(e)[:300]}")
        raise e

def query_gemini(prompt: str, system_prompt: str = None) -> str:
    """Query Groq (Llama 3 70B) with the given prompt"""
    final_system = system_prompt or SYSTEM_PROMPT

    try:
        response_text = _call_groq(
            prompt=prompt,
            system_prompt=final_system,
            json_mode=False,
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        if response_text:
            return response_text
        else:
            print("⚠️ Groq returned empty response.")
            return "The AI could not generate a response for this query. Please rephrase."
    except Exception as e:
        print(f"✗ Groq API error in query_gemini: {e}")
        traceback.print_exc()
        return "I apologize, but I'm having trouble processing your request right now. Please try again."

def query_gemini_json(prompt: str, system_prompt: str = None) -> dict:
    """Query Groq and parse structured JSON response"""
    final_system = (system_prompt or SYSTEM_PROMPT) + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no extra text."

    try:
        response_text = _call_groq(
            prompt=prompt,
            system_prompt=final_system,
            json_mode=True,
            model="llama-3.1-8b-instant", # Faster for JSON extraction
            temperature=0.1
        )
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Groq"}
    except Exception as e:
        print(f"✗ Groq JSON API error: {e}")
        traceback.print_exc()
        return {"error": str(e)}

def classify_intent(query: str) -> str:
    """Use Groq to classify user query intent for routing"""
    classification_prompt = f"""Classify the following user query into exactly ONE category.

Categories:
- DATABASE: Questions about specific crimes, cases, statistics, counts, filtering data, criminals, offenders
- NETWORK: Questions about criminal relationships, connections, associates, gangs, networks
- PREDICTION: Questions about forecasts, hotspots, trends, future crime patterns, risk areas
- REPORT: Requests to analyze, summarize, or generate investigation reports

User Query: "{query}"

Respond with ONLY the category name (DATABASE, NETWORK, PREDICTION, or REPORT). Nothing else."""

    try:
        response_text = _call_groq(
            prompt=classification_prompt,
            system_prompt="You are a strict classifier.",
            json_mode=False,
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=10
        )
        intent = response_text.strip().upper()
        # Clean up any quotes or extra text
        for valid in ["DATABASE", "NETWORK", "PREDICTION", "REPORT"]:
            if valid in intent:
                return valid
        return "DATABASE"  # fallback
    except Exception as e:
        print(f"✗ classify_intent error, using heuristic fallback: {e}")
        ql = query.lower()
        if any(w in ql for w in ['predict', 'forecast', 'future', 'trend', 'hotspot']): return "PREDICTION"
        if any(w in ql for w in ['network', 'gang', 'associate', 'connection', 'link', 'shared']): return "NETWORK"
        if any(w in ql for w in ['report', 'summary', 'brief']): return "REPORT"
        return "DATABASE"

def extract_query_parameters(query: str) -> dict:
    """Use Groq to map a query to a specific analytic tool and extract entities."""
    prompt = f"""Extract parameters for crime analysis tools from the query.
Available Tools:
1. TOP_OFFENDERS_BY_CRIME: "Who committed the most murders?", "Top cybercrime offenders"
2. GANG_SEARCH: "Show burglary gang active in Mysuru", "Find robbery gang in Bengaluru"
3. SHARED_PHONE_NETWORK: "Crimes associated with phone 9845012345"
4. GENERAL_SQL_FALLBACK: Complex questions not covered above.
5. RAG_SEARCH: General unstructured questions (e.g. "what is the procedure for...").

User Query: "{query}"

Analyze the query and respond ONLY with JSON containing:
{{
  "tool": "TOP_OFFENDERS_BY_CRIME" | "GANG_SEARCH" | "SHARED_PHONE_NETWORK" | "GENERAL_SQL_FALLBACK" | "RAG_SEARCH",
  "crime_type": "string or null",
  "district": "string or null",
  "criminal_name": "string or null",
  "phone_number": "string or null",
  "fallback_sql": "string or null (ONLY if tool is GENERAL_SQL_FALLBACK, write a safe PostgreSQL SELECT query matching the schema: crimes(id, case_id, crime_date, district, police_station_id, crime_type, description, status, lat, lng, is_resolved, resolution_date), criminals(id, name, age, gender, phone, address, criminal_history_count, is_repeat_offender, first_offense_date), crime_criminal_links(id, crime_id, criminal_id, role))"
}}"""

    try:
        response_text = _call_groq(
            prompt=prompt,
            system_prompt="You are a JSON extractor.",
            json_mode=True,
            model="llama-3.1-8b-instant",
            temperature=0.0
        )
        return json.loads(response_text)
    except Exception as e:
        print(f"✗ extract_query_parameters error, using heuristic fallback: {e}")
        ql = query.lower()
        tool = "RAG_SEARCH"
        if 'top' in ql or 'most' in ql: tool = "TOP_OFFENDERS_BY_CRIME"
        elif 'gang' in ql or 'network' in ql: tool = "GANG_SEARCH"
        elif 'phone' in ql or 'number' in ql or 'call' in ql: tool = "SHARED_PHONE_NETWORK"
        
        crime_type = None
        for ct in ['murder', 'theft', 'burglary', 'robbery', 'fraud', 'cyber', 'drug', 'assault']:
            if ct in ql: crime_type = ct.title()
            
        district = None
        for d in ['bengaluru', 'mysuru', 'mangaluru', 'hubli', 'belagavi']:
            if d in ql: district = d.title()
            
        return {"tool": tool, "crime_type": crime_type, "district": district}
