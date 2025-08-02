from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware 
from autosuggest_service import autosuggest_service
from search_service import search_service
import json

app = FastAPI(
    title="Flipkart GRID Search API",
    description="API for Autosuggest and Search Results Page systems.",
    version="1.0.0"
)

TOP_DEPARTMENTS=[]
try:
    with open('../central_data/top_departments.json', 'r') as f:
        TOP_DEPARTMENTS = json.load(f)
except FileNotFoundError:
    print("Warning: 'top_departments.json' not found. Department dropdown will be empty.")

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

@app.get("/autosuggest/departments", tags=["TopDepartments"])
def get_top_departments():
    return {"departments": TOP_DEPARTMENTS}

@app.get("/autosuggest", tags=["Autosuggest"])
def get_autosuggestions(q: str):
    if not q:
        return {"suggestions": []}
    
    suggestions = autosuggest_service.get_flipkart_style_suggestions(prefix=q)
    
    return {"suggestions": suggestions}

@app.get("/search", tags=["Search"])
def search(q: str):
    if not q:
        return {"results": [], "facets": {}}
        
    search_results = search_service.search_products(user_query=q)
    return search_results

@app.get("/api/v1/product/{asin}", tags=["Products"])
def get_product_details(asin: str):
    """
    Handles the API request to fetch a single product by its ASIN.
    """
    product = search_service.get_product_by_asin(asin=asin)
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{asin}' not found.")
    
    return {"product": product}
