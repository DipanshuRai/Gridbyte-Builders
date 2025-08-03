# Flipkart GRiD 7.0: A Modern E-Commerce Search System

**Team:** Gridbyte Builders

## 1. Overview

This is a comprehensive, high-performance e-commerce search system built as a solution for the Flipkart GRiD 7.0 challenge. It successfully delivers the two primary components required by the problem statement: a highly responsive, multi-faceted **Autosuggest** system and an intelligent, machine learning-powered **Search Results Page (SRP)**.

Our system is architected around a modern, scalable technology stack, leveraging the power of **Elasticsearch** for high-speed retrieval, **Sentence Transformers** for state-of-the-art semantic understanding, and a robust **Python (FastAPI)** backend for search logic. This is complemented by a separate **Node.js (Express)** microservice for user authentication and search history management, and a dynamic **React** frontend.

The final implementation features a sophisticated **Autosuggest** that provides users with a diverse range of suggestions (queries, products, categories, and brands) and supports both **English and Hindi** queries. The SRP is powered by a **pure semantic search ranking** model, ensuring that results are ordered by their contextual relevance, and is augmented by a dynamic presentation layer that can blend promotional content like **ads and banners** and intelligently switch between **grid and list views**.

## 2. Live Demo

[Demo Video](https://drive.google.com/file/d/1ysJt1MMp5gC0mrrnpzdClFUbdJKnvYIB/view)

## 3. Answering the Problem Statement

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
*   **Python 3.9+** and `pip`
*   **Node.js 16+** and `npm`
*   **Java Development Kit (JDK)** version 11 or newer (required by Elasticsearch)
*   A local **MongoDB** instance (or a cloud connection string)

### Step 1: Clone the Repository & Initial Setup

```bash
git clone https://github.com/DipanshuRai/Gridbyte-Builders.git
cd Gridbyte-Builders
```

### Step 2: Set Up and Run Backend Services

#### A. Download and Run Elasticsearch
1.  Download Elasticsearch 8.x from the [official website](https://www.elastic.co/downloads/elasticsearch) and unzip it to a memorable location (e.g., `C:\elasticsearch-8.x.x`).
2.  Open a dedicated terminal, navigate to the Elasticsearch directory, and run it. **Keep this terminal open.**
    ```bash
    cd C:\elasticsearch-8.x.x\bin
    ./elasticsearch.bat
    ```
3.  In browser, verify it's running:
    ```bash
    Go to "localhost:9200"
    ```
    You should see a JSON response.

#### B. Set Up the Node.js User Service
1.  Navigate to the Node.js backend directory from the project root:
    ```bash
    cd backend  # This is your Node.js user service folder
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

#### C. Set Up the Python Search Service
1.  Navigate to the Python backend directory from the project root:
    ```bash
    cd model
    ```
2.  Install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

### Step 3: Run the Data Pipeline

This is a mandatory, one-time setup process that prepares and indexes all data. **Execute these scripts from the project root in the exact order provided.**

1.  **Run Data Preparation & Indexing Scripts**:
    All the following commands should be run from the `model/data_management/` directory. Navigate there first:
    ```bash
    cd model/data_management
    ```
    Now, run the scripts in sequence:
    ```bash
    
    # 1. Generates rich, multilingual semantic embeddings
    python generate_embeddings.py
    
    # 2. Indexes the main product data into Elasticsearch
    python index_suggestions_es.py
    
    # 3. Indexes the multilingual user queries for autosuggest
    python index_multilingual_queries.py
    
    # 4. Indexes the unique categories and brands for autosuggest
    python index_entities.py
    ```

### Step 4: Run the Application

You will need three separate terminals for this step.

1.  **Start the Python Search API**:
    In a terminal, navigate to `model/backend/` and run:
    ```bash
    uvicorn app:app --reload
    ```

2.  **Start the Node.js User API**:
    In a second terminal, navigate to `backend/` (the Node.js folder) and run:
    ```bash
    npm run dev
    ```

3.  **Start the React Frontend**:
    In a third terminal, navigate to your frontend project directory (e.g., `frontend/`) and run:
    ```bash
    npm install
    npm run dev
    ```

## 6. Team Members

*   **[[Dipanshu Rai]](https://github.com/DipanshuRai)**
*   **[[Prajjwal Acharya]](https://github.com/prajjwal-acharya)**
*   **[[Megha Goswami]](https://github.com/megha-2461)**
*   **[[Keshav Mahansaria]](https://github.com/explorer-skp)**