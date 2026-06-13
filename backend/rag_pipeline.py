"""
Mocked RAG Pipeline for Hackathon Deployment
Removed PyTorch/SentenceTransformers to keep RAM usage under 512MB for Render Free Tier.
"""

def embed_and_store_crimes(crimes_df):
    """Mock storage"""
    pass

def retrieve_relevant_crimes(query, top_k=10):
    """Return mock relevant context"""
    return {
        "documents": [[
            "Recent criminal activity matches patterns seen in the region.",
            "Suspects often use shared communication channels to coordinate.",
            "Cross-district operations observed in recent months."
        ]]
    }
