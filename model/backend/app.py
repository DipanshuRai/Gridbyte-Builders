from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware 
from autosuggest_service import autosuggest_service
from search_service import search_service

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
    
    category_suggestions = []
    
    # Add top 4 departments (categories)
    facets = search_service.search_products(user_query=q, limit=0).get("facets", {})
    categories = facets.get("departments", [])
    for cat in categories[:4]:
        category_suggestions.append({
            "suggestion": cat["key"],
            "type": "category"
        })
    
    product_suggestions = autosuggest_service.get_hybrid_suggestions(prefix=q)
    final_suggestions = category_suggestions + product_suggestions

    return {"suggestions": final_suggestions}

@app.get("/search", tags=["Search"])
def search(q: str):
    if not q:
        return {"results": [], "facets": {}}
        
    search_results = search_service.search_products(user_query=q)
    return search_results
