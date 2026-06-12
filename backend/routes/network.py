from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import networkx as nx
from database import get_db_connection

router = APIRouter()

class NetworkRequest(BaseModel):
    crime_id: Optional[int] = None
    criminal_name: Optional[str] = None
    district: Optional[str] = None

@router.post("/graph")
async def get_network_graph(request: NetworkRequest):
    """Generate crime-criminal network graph from real database data"""
    conn = get_db_connection()
    if not conn:
        return {"nodes": [], "links": [], "error": "Database not connected"}

    cur = conn.cursor()
    G = nx.Graph()

    try:
        # Build query based on filters
        if request.criminal_name:
            # Search by criminal name (partial match)
            cur.execute("""
                SELECT DISTINCT c.id, c.name, c.criminal_history_count, c.is_repeat_offender, c.phone
                FROM criminals c
                WHERE LOWER(c.name) LIKE LOWER(%s)
            """, (f"%{request.criminal_name}%",))
        elif request.district:
            # Get criminals active in a specific district
            cur.execute("""
                SELECT DISTINCT c.id, c.name, c.criminal_history_count, c.is_repeat_offender, c.phone
                FROM criminals c
                JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
                JOIN crimes cr ON ccl.crime_id = cr.id
                WHERE cr.district = %s
                ORDER BY c.criminal_history_count DESC
                LIMIT 20
            """, (request.district,))
        else:
            # Default: top criminals by crime count
            cur.execute("""
                SELECT DISTINCT c.id, c.name, c.criminal_history_count, c.is_repeat_offender, c.phone
                FROM criminals c
                JOIN crime_criminal_links ccl ON c.id = ccl.criminal_id
                GROUP BY c.id, c.name, c.criminal_history_count, c.is_repeat_offender, c.phone
                ORDER BY COUNT(ccl.crime_id) DESC
                LIMIT 20
            """)

        criminals = cur.fetchall()
        criminal_ids = [c[0] for c in criminals]

        if not criminal_ids:
            return {"nodes": [], "links": [], "message": "No criminals found matching the criteria"}

        # Add criminal nodes
        for c in criminals:
            node_id = f"C{c[0]}"
            G.add_node(node_id, name=c[1], crimeCount=c[2], type="criminal",
                       isRepeat=c[3], phone=c[4] or "")

        # Get crimes linked to these criminals
        placeholders = ','.join(['%s'] * len(criminal_ids))
        cur.execute(f"""
            SELECT DISTINCT cr.id, cr.case_id, cr.crime_type, cr.district, cr.status
            FROM crimes cr
            JOIN crime_criminal_links ccl ON cr.id = ccl.crime_id
            WHERE ccl.criminal_id IN ({placeholders})
            LIMIT 30
        """, criminal_ids)

        crimes = cur.fetchall()
        crime_ids = [cr[0] for cr in crimes]

        for cr in crimes:
            node_id = f"CR{cr[0]}"
            G.add_node(node_id, name=f"{cr[2]} ({cr[3]})", crimeCount=0,
                       type="crime", caseId=cr[1], status=cr[4])

        # Get crime-criminal links
        if crime_ids:
            crime_placeholders = ','.join(['%s'] * len(crime_ids))
            cur.execute(f"""
                SELECT ccl.criminal_id, ccl.crime_id, ccl.role
                FROM crime_criminal_links ccl
                WHERE ccl.criminal_id IN ({placeholders})
                AND ccl.crime_id IN ({crime_placeholders})
            """, criminal_ids + crime_ids)

            for link in cur.fetchall():
                source = f"C{link[0]}"
                target = f"CR{link[1]}"
                if G.has_node(source) and G.has_node(target):
                    G.add_edge(source, target, role=link[2])

        # Phone-based connections
        cur.execute("""
            SELECT c1.id, c1.name, c2.id, c2.name, c1.phone
            FROM criminals c1
            JOIN criminals c2 ON c1.phone = c2.phone AND c1.id < c2.id
            WHERE c1.phone IS NOT NULL
        """)
        for row in cur.fetchall():
            source = f"C{row[0]}"
            target = f"C{row[2]}"
            if G.has_node(source) and G.has_node(target):
                G.add_edge(source, target, role=f"Shared Phone")

        # Format response
        nodes = []
        for node, data in G.nodes(data=True):
            nodes.append({
                "id": node,
                "name": data.get("name", ""),
                "crimeCount": data.get("crimeCount", 0),
                "type": data.get("type", "unknown"),
                "isRepeat": data.get("isRepeat", False),
            })

        links = []
        for u, v, data in G.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "role": data.get("role", "linked")
            })

        # Graph metrics
        metrics = {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "connected_components": nx.number_connected_components(G),
        }

        return {"nodes": nodes, "links": links, "metrics": metrics}

    except Exception as e:
        print(f"Network graph error: {e}")
        return {"nodes": [], "links": [], "error": str(e)}
    finally:
        cur.close()
        conn.close()
