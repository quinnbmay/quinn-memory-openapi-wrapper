from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from typing import Optional, Dict, Any

app = FastAPI(
    title="Quinn Memory API - OpenAPI Wrapper",
    description="OpenAPI-compliant wrapper for Quinn's personal memory system",
    version="1.0.0"
)

MEMORY_API_URL = "https://quinn-memory-api-production.up.railway.app"

class SearchRequest(BaseModel):
    user_id: str = "quinn_may"
    query: str
    limit: int = 10

class AddDataRequest(BaseModel):
    user_id: str = "quinn_may"
    data: str
    data_type: str = "text"

class ContextRequest(BaseModel):
    user_id: str = "quinn_may"
    thread_id: str = "claude"

@app.get("/health")
async def health_check():
    """Check health of both wrapper and underlying memory API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MEMORY_API_URL}/health")
            return {"status": "healthy", "memory_api": response.json()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/search")
async def search_memory(request: SearchRequest):
    """Search Quinn's personal memory graph for relevant information"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMORY_API_URL}/search",
                json={
                    "user_id": request.user_id,
                    "query": request.query,
                    "limit": request.limit
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_memory(request: AddDataRequest):
    """Add new information to Quinn's memory graph"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMORY_API_URL}/add",
                json={
                    "user_id": request.user_id,
                    "thread_id": "openwebui",
                    "messages": [{"role": "user", "content": request.data}]
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context")
async def get_context(request: ContextRequest):
    """Get user context from Quinn's memory for a specific thread"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMORY_API_URL}/context",
                json={
                    "user_id": request.user_id,
                    "thread_id": request.thread_id
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)