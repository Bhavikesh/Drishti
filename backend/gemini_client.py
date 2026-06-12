"""
Gemini 2.0 Flash client for CrimeMind AI
With automatic retry on rate limits
"""
import os
import json
import time
import traceback
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini client
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"✅ Gemini client initialized (key ends with ...{GEMINI_API_KEY[-6:]})")
    except Exception as e:
        print(f"❌ Gemini client init failed: {e}")
else:
    print("⚠️ GEMINI_API_KEY not set!")

SYSTEM_PROMPT = """You are CrimeMind AI, an intelligent crime investigation copilot for Karnataka State Police.

Your role:
- Analyze crime data and provide actionable intelligence
- Identify patterns, networks, and hotspots
- Provide explainable recommendations backed by data
- Be professional, concise, and accurate
- When presenting analysis, use structured formats with bullet points
- Always cite specific numbers and statistics from the provided data
- Suggest recommended actions for law enforcement

When providing investigation summaries, structure your response as:
**Summary:** Brief overview of findings
**Key Statistics:** Bullet points with specific numbers
**Identified Patterns:** Any trends or patterns detected
**Repeat Offenders:** Named individuals with crime counts (if applicable)
**Recommended Actions:** Specific actionable recommendations

Never fabricate data. Only use information provided in the context."""


def _call_gemini_with_retry(model, contents, config, max_retries=3):
    """Wrapper that retries on 429 rate limit errors with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            return response
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = 2 * (attempt + 1)  # Reduce wait time to 2s, 4s, 6s so UI doesn't freeze forever
                print(f"⏳ Rate limited (attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exceeded for Gemini API")


def query_gemini(prompt: str, system_prompt: str = None) -> str:
    """Query Gemini 2.0 Flash with the given prompt"""
    if not client:
        print("Warning: Gemini client not available. Using mock response.")
        return f"[Mock Response] I received your query: {prompt[:100]}..."

    final_system = system_prompt or SYSTEM_PROMPT

    try:
        response = _call_gemini_with_retry(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=final_system,
                temperature=0.7,
                max_output_tokens=1500,
            ),
        )
        if response and response.text:
            return response.text
        else:
            print(f"⚠️ Gemini returned empty response. Candidates: {response.candidates if response else 'None'}")
            return "The AI could not generate a response for this query. Please rephrase."
    except Exception as e:
        print(f"✗ Gemini API error in query_gemini: {e}")
        traceback.print_exc()
        return "I apologize, but I'm having trouble processing your request right now. Please try again."


def query_gemini_json(prompt: str, system_prompt: str = None) -> dict:
    """Query Gemini and parse structured JSON response"""
    if not client:
        return {"error": "GEMINI_API_KEY not set"}

    final_system = (system_prompt or SYSTEM_PROMPT) + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no extra text."

    try:
        response = _call_gemini_with_retry(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=final_system,
                temperature=0.3,
                max_output_tokens=2000,
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text wrapped
        return {"response": response.text if response else "No response"}
    except Exception as e:
        print(f"✗ Gemini JSON API error: {e}")
        traceback.print_exc()
        return {"error": str(e)}


def classify_intent(query: str) -> str:
    """Use Gemini to classify user query intent for routing"""
    classification_prompt = f"""Classify the following user query into exactly ONE category.

Categories:
- DATABASE: Questions about specific crimes, cases, statistics, counts, filtering data, criminals, offenders
- NETWORK: Questions about criminal relationships, connections, associates, gangs, networks
- PREDICTION: Questions about forecasts, hotspots, trends, future crime patterns, risk areas
- REPORT: Requests to analyze, summarize, or generate investigation reports

User Query: "{query}"

Respond with ONLY the category name (DATABASE, NETWORK, PREDICTION, or REPORT). Nothing else."""

    if not client:
        return "DATABASE"

    try:
        response = _call_gemini_with_retry(
            model="gemini-2.0-flash",
            contents=classification_prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=20,
            ),
        )
        intent = response.text.strip().upper()
        if intent in ["DATABASE", "NETWORK", "PREDICTION", "REPORT"]:
            return intent
        return "DATABASE"  # fallback
    except Exception as e:
        print(f"✗ classify_intent error, using heuristic fallback: {e}")
        # Heuristic fallback
        ql = query.lower()
        if any(w in ql for w in ['predict', 'forecast', 'future', 'trend', 'hotspot']): return "PREDICTION"
        if any(w in ql for w in ['network', 'gang', 'associate', 'connection', 'link', 'shared']): return "NETWORK"
        if any(w in ql for w in ['report', 'summary', 'brief']): return "REPORT"
        return "DATABASE"


def extract_query_parameters(query: str) -> dict:
    """Use Gemini to map a query to a specific analytic tool and extract entities."""
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

    if not client:
        return {"tool": "RAG_SEARCH"}
        
    try:
        response = _call_gemini_with_retry(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=500,
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"✗ extract_query_parameters error, using heuristic fallback: {e}")
        # Heuristic fallback
        ql = query.lower()
        tool = "RAG_SEARCH"
        if 'top' in ql or 'most' in ql: tool = "TOP_OFFENDERS_BY_CRIME"
        elif 'gang' in ql or 'network' in ql: tool = "GANG_SEARCH"
        elif 'phone' in ql or 'number' in ql or 'call' in ql: tool = "SHARED_PHONE_NETWORK"
        
        # Very simple extraction
        crime_type = None
        for ct in ['murder', 'theft', 'burglary', 'robbery', 'fraud', 'cyber', 'drug', 'assault']:
            if ct in ql: crime_type = ct.title()
            
        district = None
        for d in ['bengaluru', 'mysuru', 'mangaluru', 'hubli', 'belagavi']:
            if d in ql: district = d.title()
            
        return {"tool": tool, "crime_type": crime_type, "district": district}
