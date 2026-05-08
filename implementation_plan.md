# Implementation Plan: Problem B (NLP-to-SQL Semantic Layer)

## 1. System Architecture

The solution will consist of three main components:
1.  **Semantic Layer (`semantic_layer.yaml`)**: A configuration file acting as a bridge between the raw database schema and the LLM. It defines tables, descriptions, relationships, business metrics, and synonyms.
2.  **Query Engine (`query_engine.py`)**: The core Python module that:
    *   Loads the semantic layer.
    *   Constructs a highly-engineered prompt for the LLM.
    *   Handles ambiguity (detecting vague terms and stating assumptions or asking for clarification).
    *   Executes the generated SQL against the SQLite database.
    *   Generates a plain-English explanation of the results.
3.  **User Interface (`app.py`)**: A Streamlit web application providing a clean, interactive chat interface where users can ask questions, view the generated SQL, see the data table, and read the explanation.

## 2. Step-by-Step Implementation

### Step 1: Auto-Discover & Define the Semantic Layer
*   **Action**: Write a script (`schema_extractor.py`) to connect to `cashflo_sample.db`, extract all table schemas and foreign keys, and dump an initial `semantic_layer.yaml`.
*   **Action**: Manually refine the YAML. Add business contexts like synonyms (e.g., `bills` -> `invoices`), relationships, and explicit metrics (e.g., `revenue` and `outstanding` as defined in the prompt).

### Step 2: Build the Core NLP-to-SQL Engine
*   **Action**: Create `query_engine.py`. We will use a structured output approach with the LLM (using the `openai` or `anthropic` Python SDK).
*   **Action**: Define the LLM Prompt. The prompt will provide the semantic schema and instruct the LLM to output a JSON object containing:
    ```json
    {
       "sql": "SELECT ...",
       "is_ambiguous": false,
       "assumptions_made": ["Assumed 'last quarter' refers to Q1 2024"],
       "clarification_needed": null
    }
    ```
*   **Action**: Implement the database execution logic. Catch SQL execution errors and optionally feed them back to the LLM for self-correction (Error Handling).

### Step 3: Implement Ambiguity & Explanation Handling
*   **Action**: Add a secondary LLM call (or include it in the primary) to generate a human-readable explanation of the SQL (e.g., "I'm looking at the invoices table...").
*   **Action**: Implement logic that if `is_ambiguous` is true, the system pauses and asks the user the `clarification_needed` question instead of executing a random query.

### Step 4: Build the Interactive UI (Bonus points for aesthetics)
*   **Action**: Build `app.py` using Streamlit.
*   **Action**: Implement a chat interface.
*   **Action**: Display results dynamically: if the engine returns SQL, show the SQL code block, the data in a dataframe, and the plain-English explanation.

### Step 5: Final Polish & README
*   **Action**: Create the required `README.md` containing architecture overview, AI tools used, sample runs, and known limitations.
*   **Action**: Provide clear setup instructions.

## 3. Technology Stack
*   **Language**: Python 3.10+
*   **Database**: SQLite (`cashflo_sample.db`)
*   **LLM Integration**: OpenAI API using `python-dotenv` for configuration. 
    *   **Primary Model**: `gpt-4o` is recommended as the primary model for generating the SQL queries. It handles complex joins, window functions, and ambiguity reasoning significantly better than smaller models.
    *   **Secondary Model**: `gpt-4o-mini` can optionally be used for generating the plain-English explanations to save on costs and latency.
*   **UI Framework**: Streamlit

