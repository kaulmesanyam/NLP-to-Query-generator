# Semantic Layer on a Database for NLP-to-Query Conversion

## Overview
This repository contains a solution for **Semantic Layer on a Database for NLP-to-Query Conversion**.
The solution implements an AI-powered text-to-SQL assistant that allows business users to query their Accounts Payable (AP) data using natural language.

## Architecture
The system consists of three main components:
1.  **Semantic Layer (`semantic_layer.yaml`)**: An auto-discovered and manually refined configuration that maps the raw database schema (`cashflo_sample.db`) to business concepts. It includes:
    *   Descriptions for tables and columns.
    *   Pre-defined multi-table relationships (joins).
    *   Business synonyms (e.g., "bills" -> "invoices").
    *   Explicit metric calculations (e.g., `revenue`, `outstanding`).
2.  **Query Engine (`query_engine.py`)**: A Python module that takes a user query and the semantic layer, injects them into a highly structured prompt, and uses OpenAI's API (with `pydantic` Structured Outputs) to generate:
    *   The SQL query.
    *   Any assumptions made.
    *   Ambiguity detection (clarification questions).
    *   A plain-English explanation of the SQL.
3.  **User Interface (`app.py`)**: An interactive chat interface built with Streamlit for a seamless user experience.

## Setup Instructions
1. **Prerequisites**: Python 3.10+
2. **Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-...
   ```
5. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## AI Tools Used
*   **Antigravity (Gemini 3.1 Pro (Low))**: Used as the primary AI coding assistant to scaffold the project structure, generate the initial SQLite schema extractor, formulate the LLM prompt inside `query_engine.py`, and build the Streamlit UI.
*   **OpenAI (`gpt-4o`)**: Acts as the core intelligence engine for generating the SQLite queries from the semantic layer.

## Known Limitations & Tradeoffs
1. **Database Size Limits**: The schema is injected directly into the LLM context. For databases with thousands of tables, this approach would hit token limits and require a Retrieval-Augmented Generation (RAG) approach to retrieve only relevant schema parts.
2. **Error Handling**: Currently, if the generated SQL is invalid, it simply returns the SQLite error. A more robust solution would feed the error back to the LLM for a self-correction retry loop.
3. **Read-Only**: The current connection doesn't explicitly restrict PRAGMA or WRITE operations. In production, the engine must execute against a strict read-only replica.
