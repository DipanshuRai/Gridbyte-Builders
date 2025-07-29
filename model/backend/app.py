from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .autosuggest_service import autosuggest_service
from .search_service import search_service

from fastapi.responses import JSONResponse
from fastapi.requests import Request
import traceback

app = FastAPI(
    title="Flipkart GRID Search API",
    description="API for Autosuggest and Search Results Page systems.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Flipkart Search API"}

@app.get("/autosuggest", tags=["Autosuggest"])
def get_autosuggestions(q: str):
    if not q:
        return {"suggestions": []}
    
    suggestions = autosuggest_service.get_suggestions(prefix=q)
    
    # 🔄 Get related categories (departments) using same query
    facets = search_service.search_products(user_query=q, limit=0).get("facets", {})
    categories = facets.get("departments", [])

    for cat in categories[:4]:  # Limit to top 4 categories
        suggestions.append({
            "suggestion": cat["key"],
            "type": "category"
        })
    
    return {"suggestions": suggestions}

# @app.get("/autosuggest", tags=["Autosuggest"])
# def get_autosuggestions(q: str):
#     if not q:
#         return []
    
#     suggestions = autosuggest_service.get_suggestions(prefix=q)
#     return {"suggestions": suggestions}

@app.get("/search", tags=["Search"])
def search(q: str):
    if not q:
        return {"results": [], "facets": {}}
        
    search_results = search_service.search_products(user_query=q)
    return search_results


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 Unhandled Exception:", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )