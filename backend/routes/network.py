from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import networkx as nx

router = APIRouter()

class NetworkRequest(BaseModel):
    crime_id: Optional[int] = None
    criminal_name: Optional[str] = None

@router.post("/graph")
async def get_network_graph(request: NetworkRequest):
    # Mock data for hackathon
    G = nx.Graph()
    
    # Add nodes
    G.add_node("C1", name="Raju", crimeCount=5, type="criminal")
    G.add_node("C2", name="Ramesh", crimeCount=2, type="criminal")
    G.add_node("CR1", name="Theft in Indiranagar", crimeCount=0, type="crime")
    G.add_node("CR2", name="Robbery in Koramangala", crimeCount=0, type="crime")
    
    # Add edges
    G.add_edge("C1", "CR1")
    G.add_edge("C1", "CR2")
    G.add_edge("C2", "CR1")
    
    nodes = []
    for node, data in G.nodes(data=True):
        nodes.append({"id": node, "name": data.get("name", ""), "crimeCount": data.get("crimeCount", 0)})
        
    links = []
    for u, v in G.edges():
        links.append({"source": u, "target": v})
        
    return {"nodes": nodes, "links": links}
