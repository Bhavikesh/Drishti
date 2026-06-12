"""
CrimeMind AI — LangGraph-style Router (4-Node Architecture)

Routes user queries to specialized agents:
  Router → Database Agent | Network Agent | Prediction Agent | Report Agent

Kept simple and functional for hackathon — no complex orchestration.
"""
import json
from database import get_db_connection
import gemini_client
import rag_pipeline
import analytics_tools


def route_query(user_query: str, session_context: list = None) -> dict:
    """
    Main entry point. Classifies intent and routes to the right agent.
    Returns a rich response dict.
    """
    intent = gemini_client.classify_intent(user_query)
    print(f"🧠 Intent classified: {intent}")

    # Get RAG context for all queries
    try:
        rag_results = rag_pipeline.retrieve_relevant_crimes(user_query, top_k=15)
        rag_text = "\n".join(rag_results['documents'][0]) if rag_results and rag_results['documents'][0] else ""
        rag_sources = rag_results.get('metadatas', [[]])[0] if rag_results else []
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        rag_text = ""
        rag_sources = []

    # Route to specialized agent
    if intent in ["DATABASE", "NETWORK"]:
        return dynamic_analytics_agent(user_query, rag_text, rag_sources)
    elif intent == "PREDICTION":
        return prediction_agent(user_query, rag_text, rag_sources)
    elif intent == "REPORT":
        return report_agent(user_query, rag_text, rag_sources)
    else:
        return dynamic_analytics_agent(user_query, rag_text, rag_sources)


def dynamic_analytics_agent(query: str, rag_context: str, sources: list) -> dict:
    """Handles specific SQL analytic queries dynamically using strict tools."""
    
    # 1. Extract intent and parameters
    params = gemini_client.extract_query_parameters(query)
    tool = params.get("tool", "RAG_SEARCH")
    
    print(f"🛠️  Using Analytic Tool: {tool} with params: {params}")
    
    # 2. Execute corresponding robust SQL template
    sql_results = {}
    if tool == "TOP_OFFENDERS_BY_CRIME":
        sql_results = analytics_tools.get_top_offenders_by_crime(params.get("crime_type"), params.get("district"))
    elif tool == "GANG_SEARCH":
        sql_results = analytics_tools.get_gang_members(params.get("district"), params.get("crime_type"))
    elif tool == "SHARED_PHONE_NETWORK":
        sql_results = analytics_tools.get_phone_network(params.get("phone_number"))
    elif tool == "GENERAL_SQL_FALLBACK":
        fallback_sql = params.get("fallback_sql")
        if fallback_sql:
            sql_results = analytics_tools.execute_fallback_sql(fallback_sql)
        else:
            sql_results = {"error": "No fallback SQL generated"}
    else:
        # RAG Search or unknown - fetch basic stats just in case
        sql_results = _get_crime_stats(query)

    # 3. Explain the results with Gemini
    prompt = f"""You are the Analytic Agent of CrimeMind AI.
    
The user asked: "{query}"

=== DATABASE SQL QUERY RESULTS ===
{json.dumps(sql_results, indent=2, default=str)}

=== RELEVANT RAG RECORDS ===
{rag_context[:1500]}

Please provide a clear, exact answer to the user's question. 
If the SQL results contain the answer (e.g., names of criminals or gangs), YOU MUST LIST THEM EXACTLY AS THEY APPEAR in the database results.
Do NOT say "I cannot identify names" if the names are in the SQL results!
Keep it professional, concise, and formatted beautifully with bullet points if applicable."""

    response = gemini_client.query_gemini(prompt)

    return {
        "response": response,
        "sources": sources[:5],
        "confidence": 0.95 if tool != "RAG_SEARCH" else 0.85,
        "agent": f"ANALYTICS ({tool})",
        "sql_results": sql_results
    }


def prediction_agent(query: str, rag_context: str, sources: list) -> dict:
    """Handles hotspot detection, forecasting, and trend analysis"""
    prediction_data = _get_prediction_data(query)

    prompt = f"""You are the Predictive Intelligence Agent of CrimeMind AI.

The user wants crime forecasts, hotspot analysis, or trend predictions.

=== CRIME TREND DATA ===
{json.dumps(prediction_data, indent=2, default=str)}

=== RELEVANT CRIME RECORDS ===
{rag_context[:2000]}

=== USER QUERY ===
{query}

Provide an EXPLAINABLE prediction with:
1. **Hotspot Risk Level**: HIGH / MEDIUM / LOW
2. **Key Statistics**: Specific numbers backing the prediction
3. **Reasons**: 3-4 bullet points explaining WHY this prediction is made
4. **Historical Pattern**: Compare with previous period
5. **Recommended Action**: Specific policing recommendations

Be data-driven. Cite exact numbers."""

    response = gemini_client.query_gemini(prompt)

    return {
        "response": response,
        "sources": sources[:5],
        "confidence": 0.85,
        "agent": "PREDICTION",
        "prediction_data": prediction_data
    }


def report_agent(query: str, rag_context: str, sources: list) -> dict:
    """Generates comprehensive investigation summaries"""
    # Gather data from all sources
    db_stats = _get_crime_stats(query)
    network_data = _get_network_data(query)
    prediction_data = _get_prediction_data(query)

    prompt = f"""You are the Investigation Report Agent of CrimeMind AI.

Generate a comprehensive investigation summary for the user's query.

=== DATABASE STATISTICS ===
{json.dumps(db_stats, indent=2, default=str)}

=== CRIMINAL NETWORK DATA ===
{json.dumps(network_data, indent=2, default=str)}

=== CRIME TREND DATA ===
{json.dumps(prediction_data, indent=2, default=str)}

=== RELEVANT CRIME RECORDS ===
{rag_context[:2000]}

=== USER QUERY ===
{query}

Generate a structured investigation report:

**📋 Investigation Summary**
Brief overview (2-3 sentences)

**📊 Key Statistics**
- Total cases found
- Resolution rate
- Most common crime type
- Time period covered

**👤 Identified Suspects / Repeat Offenders**
- Name, crime count, repeat offender status

**🔥 Hotspot Areas**
- Top locations with case counts

**📈 Trend Analysis**
- Month-over-month change
- Predicted direction

**⚠️ Risk Assessment**
- Overall risk level with explanation

**🎯 Recommended Actions**
- 3-5 specific, actionable recommendations for law enforcement

Use specific numbers from the data. This report should feel like professional police intelligence."""

    response = gemini_client.query_gemini(prompt)

    return {
        "response": response,
        "sources": sources[:5],
        "confidence": 0.90,
        "agent": "REPORT",
        "stats": db_stats,
        "network_data": network_data,
        "prediction_data": prediction_data
    }


# ============================================================
# Helper functions to fetch data from Supabase
# ============================================================

def _get_crime_stats(query: str) -> dict:
    """Fetch crime statistics from the database"""
    conn = get_db_connection()
    if not conn:
        return {"error": "DB not connected"}

    cur = conn.cursor()
    stats = {}

    try:
        # Total crimes
        cur.execute("SELECT COUNT(*) FROM crimes")
        stats['total_crimes'] = cur.fetchone()[0]

        # Resolution rate
        cur.execute("SELECT COUNT(*) FROM crimes WHERE is_resolved = true")
        resolved = cur.fetchone()[0]
        stats['resolved_crimes'] = resolved
        stats['resolution_rate'] = f"{(resolved / max(stats['total_crimes'], 1)) * 100:.1f}%"

        # Active cases
        cur.execute("SELECT COUNT(*) FROM crimes WHERE status = 'Under Investigation'")
        stats['active_cases'] = cur.fetchone()[0]

        # By crime type
        cur.execute("SELECT crime_type, COUNT(*) as cnt FROM crimes GROUP BY crime_type ORDER BY cnt DESC")
        stats['by_crime_type'] = [{'type': r[0], 'count': r[1]} for r in cur.fetchall()]

        # By district
        cur.execute("SELECT district, COUNT(*) as cnt FROM crimes GROUP BY district ORDER BY cnt DESC")
        stats['by_district'] = [{'district': r[0], 'count': r[1]} for r in cur.fetchall()]

        # Repeat offenders
        cur.execute("""
            SELECT c.name, c.criminal_history_count, COUNT(ccl.id) as linked_cases
            FROM criminals c
            JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
            WHERE c.is_repeat_offender = true
            GROUP BY c.id, c.name, c.criminal_history_count
            ORDER BY linked_cases DESC
            LIMIT 10
        """)
        stats['top_repeat_offenders'] = [{'name': r[0], 'history': r[1], 'linked_cases': r[2]} for r in cur.fetchall()]

        # Extract district/crime type from query for filtered stats
        query_lower = query.lower()
        for district in ['bengaluru', 'mysuru', 'mangaluru', 'hubli', 'belagavi', 'kalaburagi', 'vijayapura', 'tumakuru', 'shivamogga', 'ballari']:
            if district in query_lower:
                # Map short names
                district_map = {'bengaluru': 'Bengaluru Urban', 'mysuru': 'Mysuru', 'mangaluru': 'Mangaluru',
                                'hubli': 'Hubli-Dharwad', 'belagavi': 'Belagavi', 'kalaburagi': 'Kalaburagi',
                                'vijayapura': 'Vijayapura', 'tumakuru': 'Tumakuru', 'shivamogga': 'Shivamogga',
                                'ballari': 'Ballari'}
                full_name = district_map.get(district, district.title())
                cur.execute("SELECT crime_type, COUNT(*) FROM crimes WHERE district = %s GROUP BY crime_type ORDER BY COUNT(*) DESC", (full_name,))
                stats['filtered_by_district'] = {'district': full_name, 'crimes': [{'type': r[0], 'count': r[1]} for r in cur.fetchall()]}
                break

    except Exception as e:
        stats['error'] = str(e)
    finally:
        cur.close()
        conn.close()

    return stats


def _get_network_data(query: str) -> dict:
    """Fetch criminal network data from the database"""
    conn = get_db_connection()
    if not conn:
        return {"nodes": [], "links": []}

    cur = conn.cursor()
    data = {"nodes": [], "links": []}

    try:
        # Get criminals linked to crimes matching the query context
        cur.execute("""
            SELECT DISTINCT c.id, c.name, c.criminal_history_count, c.is_repeat_offender, c.phone,
                   COUNT(ccl.crime_id) as crime_count
            FROM criminals c
            JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
            GROUP BY c.id, c.name, c.criminal_history_count, c.is_repeat_offender, c.phone
            ORDER BY crime_count DESC
            LIMIT 20
        """)

        criminals = cur.fetchall()
        criminal_ids = [c[0] for c in criminals]

        for c in criminals:
            data['nodes'].append({
                'id': f'criminal_{c[0]}',
                'name': c[1],
                'type': 'criminal',
                'crimeCount': c[5],
                'isRepeat': c[3],
                'phone': c[4]
            })

        if criminal_ids:
            # Get crimes linked to these criminals
            placeholders = ','.join(['%s'] * len(criminal_ids))
            cur.execute(f"""
                SELECT DISTINCT cr.id, cr.case_id, cr.crime_type, cr.district
                FROM crimes cr
                JOIN crime_criminal_links ccl ON cr.id = ccl.crime_id
                WHERE ccl.criminal_id IN ({placeholders})
                LIMIT 30
            """, criminal_ids)

            crimes = cur.fetchall()
            for cr in crimes:
                data['nodes'].append({
                    'id': f'crime_{cr[0]}',
                    'name': f'{cr[2]} - {cr[3]}',
                    'type': 'crime',
                    'crimeCount': 0,
                    'caseId': cr[1]
                })

            # Get links
            cur.execute(f"""
                SELECT ccl.criminal_id, ccl.crime_id, ccl.role
                FROM crime_criminal_links ccl
                WHERE ccl.criminal_id IN ({placeholders})
                AND ccl.crime_id IN (
                    SELECT DISTINCT cr.id FROM crimes cr
                    JOIN crime_criminal_links ccl2 ON cr.id = ccl2.crime_id
                    WHERE ccl2.criminal_id IN ({placeholders})
                    LIMIT 30
                )
            """, criminal_ids + criminal_ids)

            for link in cur.fetchall():
                data['links'].append({
                    'source': f'criminal_{link[0]}',
                    'target': f'crime_{link[1]}',
                    'role': link[2]
                })

            # Phone-based connections (criminals sharing phone numbers)
            cur.execute("""
                SELECT c1.id, c1.name, c2.id, c2.name, c1.phone
                FROM criminals c1
                JOIN criminals c2 ON c1.phone = c2.phone AND c1.id < c2.id
                WHERE c1.phone IS NOT NULL
                LIMIT 15
            """)
            for row in cur.fetchall():
                data['links'].append({
                    'source': f'criminal_{row[0]}',
                    'target': f'criminal_{row[2]}',
                    'role': f'Shared Phone: {row[4]}'
                })

    except Exception as e:
        data['error'] = str(e)
    finally:
        cur.close()
        conn.close()

    return data


def _get_prediction_data(query: str) -> dict:
    """Fetch data needed for predictions and hotspot analysis"""
    conn = get_db_connection()
    if not conn:
        return {"error": "DB not connected"}

    cur = conn.cursor()
    data = {}

    try:
        # Monthly crime trends
        cur.execute("""
            SELECT TO_CHAR(crime_date, 'YYYY-MM') as month, COUNT(*) as count
            FROM crimes
            GROUP BY month
            ORDER BY month
        """)
        data['monthly_trends'] = [{'month': r[0], 'count': r[1]} for r in cur.fetchall()]

        # Hotspots by district
        cur.execute("""
            SELECT district, crime_type, COUNT(*) as count
            FROM crimes
            GROUP BY district, crime_type
            ORDER BY count DESC
            LIMIT 20
        """)
        data['hotspots'] = [{'district': r[0], 'crime_type': r[1], 'count': r[2]} for r in cur.fetchall()]

        # Top stations by crime count
        cur.execute("""
            SELECT ps.name, ps.district, COUNT(cr.id) as crime_count, ps.lat, ps.lng
            FROM police_stations ps
            JOIN crimes cr ON cr.police_station_id = ps.id
            GROUP BY ps.id, ps.name, ps.district, ps.lat, ps.lng
            ORDER BY crime_count DESC
            LIMIT 10
        """)
        data['top_stations'] = [{'station': r[0], 'district': r[1], 'count': r[2], 'lat': r[3], 'lng': r[4]} for r in cur.fetchall()]

        # Recent month vs previous month comparison
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE crime_date >= CURRENT_DATE - INTERVAL '30 days') as recent,
                COUNT(*) FILTER (WHERE crime_date >= CURRENT_DATE - INTERVAL '60 days' AND crime_date < CURRENT_DATE - INTERVAL '30 days') as previous
            FROM crimes
        """)
        row = cur.fetchone()
        if row:
            recent, previous = row[0] or 0, row[1] or 0
            change = ((recent - previous) / max(previous, 1)) * 100
            data['month_comparison'] = {
                'recent_month_count': recent,
                'previous_month_count': previous,
                'change_percent': f"{change:+.1f}%"
            }

        # Active repeat offenders
        cur.execute("""
            SELECT c.name, c.criminal_history_count, COUNT(ccl.id) as active_cases
            FROM criminals c
            JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
            JOIN crimes cr ON ccl.crime_id = cr.id
            WHERE c.is_repeat_offender = true AND cr.status != 'Closed'
            GROUP BY c.id, c.name, c.criminal_history_count
            ORDER BY active_cases DESC
            LIMIT 10
        """)
        data['active_repeat_offenders'] = [{'name': r[0], 'history': r[1], 'active_cases': r[2]} for r in cur.fetchall()]

    except Exception as e:
        data['error'] = str(e)
    finally:
        cur.close()
        conn.close()

    return data
