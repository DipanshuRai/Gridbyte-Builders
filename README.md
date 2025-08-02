# Flipkart GRiD 7.0: A Modern E-Commerce Search System

**Team:** Gridbyte Builders

## 1. Overview

This is a comprehensive, high-performance e-commerce search system built as a solution for the Flipkart GRiD 7.0 challenge. It successfully delivers the two primary components required by the problem statement: a highly responsive, multi-faceted **Autosuggest** system and an intelligent, machine learning-powered **Search Results Page (SRP)**.

Our system is architected around a modern, scalable technology stack, leveraging the power of **Elasticsearch** for high-speed retrieval, **Sentence Transformers** for state-of-the-art semantic understanding, and a robust **Python (FastAPI)** backend for search logic. This is complemented by a separate **Node.js (Express)** microservice for user authentication and search history management, and a dynamic **React** frontend.

The final implementation features a sophisticated **Autosuggest** that provides users with a diverse range of suggestions (queries, products, categories, and brands) and supports both **English and Hindi** queries. The SRP is powered by a **pure semantic search ranking** model, ensuring that results are ordered by their contextual relevance, and is augmented by a dynamic presentation layer that can blend promotional content like **ads and banners** and intelligently switch between **grid and list views**.

## 2. Live Demo

[![Project Demo Video](https://img.youtube.com/vi/YOUR_YOUTUBE_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID)

**Click the image above to watch a 3-minute video demonstration of the project.**

*(Note: To use the thumbnail, replace `YOUTUBE_VIDEO_ID` with the ID of YouTube video, e.g., `dQw4w9WgXcQ`)*

## 3. Answering the Hackathon Problem Statement

Our project is a direct and comprehensive answer to the challenge, addressing every specified objective.

### A. The Autosuggest System

*   **Gleaning User Intent:** We implemented a **multi-entity suggestion architecture**. Our `autosuggest_service` orchestrates calls to four separate, specialized Elasticsearch indices to fetch popular queries, semantically relevant products, navigational categories, and matching brands.
*   **Reducing Typing Effort & Handling Typos:** Our `queries_index` is powered by Elasticsearch's Completion Suggester, configured with `fuzzy` search to automatically handle spelling mistakes.
*   **Ranking with Confidence:** Our offline pipeline aggregates user search logs and uses query frequency as a `weight`, ensuring that popular and high-performing search terms are ranked higher.
*   **Multilingual Support:** The system detects whether a query is in English or Hindi and queries the appropriate language-specific fields in Elasticsearch, providing relevant suggestions for both.

### B. The Search Results Page (SRP) System

*   **Query Understanding:** We generate a rich **"semantic fingerprint"** for each product by creating a vector embedding from its title, description, and key specifications in both English and Hindi. This allows our system to match queries based on contextual meaning.
*   **Product Retrieval:** We use a **hybrid retrieval strategy**, combining traditional keyword matching (`multi_match`) with modern semantic vector search (`knn`) to retrieve a strong set of initial candidates.
*   **Ranking of Products:** We implemented a **pure semantic ranking** model. The retrieved candidates are sorted based on the **cosine similarity** between the user's query embedding and each product's rich embedding, guaranteeing that the most contextually relevant products are ranked highest.
*   **Presentation Layer:** Our API is designed to power a rich UI. It seamlessly blend ads and banners, returns **facets** to dynamically build the filter sidebar, and provides a `view_preference` ("grid" or "list") to adapt the layout.

## 4. System Architecture and Technology Stack

Our project utilizes a modern, robust, and scalable **microservices-based architecture**, allowing for the independent development and scaling of different system components.

![Architecture Diagram](path/to/your/architecture_diagram.png)  

### Frontend (UI Layer)
*   **Technology:** **React**
*   **Responsibilities:** A dynamic and responsive user interface that serves as the single point of interaction for the user.

### Backend - User & History Service
*   **Technology:** **Node.js** with the **Express.js** framework.
*   **Database:** **MongoDB**
*   **Responsibilities:** Handles all user authentication with JWT, manages user data, and saves all user search queries to a history collection.

### Backend - Search & Discovery Service
*   **Technology:** **Python** with the **FastAPI** framework.
*   **Responsibilities:** Encapsulates all complex business logic for autosuggestions, search, product ranking, and the blending of promotional content.

### Data & Machine Learning Layer
*   **Elasticsearch:** The core of our search system, used as a high-speed engine for product retrieval. It leverages multiple specialized indices (`products`, `queries`, `categories`, `brands`) to optimize performance.
*   **Sentence-Transformers:** A Python library used to access the `paraphrase-multilingual-MiniLM-L12-v2` model for generating powerful, multilingual semantic vector embeddings.
*   **Pandas & Scikit-learn:** These libraries form the backbone of our extensive offline data processing pipeline, used for data cleaning, synthetic data generation, and feature engineering.

## 5. Setup and Execution Instructions

Follow these steps precisely to set up and run the entire project.

### Prerequisites
*   Python 3.9+
*   Node.js 16+
*   Docker and Docker Compose (for Elasticsearch) or a local Elasticsearch 8.x installation
*   MongoDB (local or cloud instance)

### Step 1: Clone the Repository
```bash
git clone https://github.com/DipanshuRai/Gridbyte-Builders.git
cd Gridbyte-Builders
```

### Step 2: Set Up Backend Services

#### A. Start Elasticsearch and MongoDB
Ensure your Elasticsearch and MongoDB instances are running. If using Docker, a `docker-compose.yml` file may be provided.
```bash
# Example if using Docker
docker-compose up -d
```
Verify Elasticsearch is running by navigating to `http://localhost:9200` in your browser.

#### B. Set Up the Python Search Service
1.  Navigate to the Python backend directory:
    ```bash
    cd model/backend
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

#### C. Set Up the Node.js User Service
1.  Navigate to the Node.js backend directory:

2.  Install dependencies:
    ```bash
    npm install
    ```

### Step 3: Run the Data Pipeline

This is a mandatory, one-time setup process that prepares all the data for the search engine. **Execute these scripts in the exact order provided.**

1.  **Delete Old Indices (Important!)**:
    Open a new terminal and run the following commands to ensure a clean slate:
    ```bash
    curl -X DELETE "localhost:9200/products_index"
    curl -X DELETE "localhost:9200/queries_index"
    curl -X DELETE "localhost:9200/categories_index"
    curl -X DELETE "localhost:9200/brands_index"
    ```

2.  **Run Data Preparation Scripts**:
    Navigate to the `model/data_management/` directory.
    ```bash
    # 1. Clean data, generate synthetic features, and create translations
    python prepare_data.py
    
    # 2. Add calculated features like quality_score
    python add_ranking_features.py
    
    # 3. Create supporting datasets and user history
    python create_specialized_datasets.py
    
    # 4. Generate the simulated user search log
    python generate_query_log.py
    
    # 5. Generate rich, multilingual semantic embeddings
    python generate_embeddings.py
    ```

3.  **Run Indexing Scripts**:
    Stay in the `model/data_management/` directory.
    ```bash
    # 6. Index the main product data
    python index_suggestions_es.py
    
    # 7. Index the multilingual user queries for autosuggest
    python index_queries.py
    
    # 8. Index the unique categories and brands for autosuggest
    python index_entities.py
    ```

### Step 4: Run the Application

1.  **Start the Python Search API**:
    In the `model/backend/` directory, run:
    ```bash
    uvicorn app:app --reload
    ```

2.  **Start the Node.js User API**:
    In the `/backend` directory, run:
    ```bash
    npm run dev
    ```

3.  **Start the React Frontend**:
    Navigate to your frontend project directory.
    
    ```bash
    npm start
    ```

## 6. Team Members

*   **[[Dipanshu Rai]](https://github.com/DipanshuRai)**
*   **[[Prajjwal Acharya]](https://github.com/prajjwal-acharya)**
*   **[[Megha Goswami]](https://github.com/megha-2461)**
*   **[[Keshav Mahansaria]](https://github.com/explorer-skp)**