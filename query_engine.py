import sqlite3
import yaml
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import pandas as pd

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = 'cashflo_sample.db'
SEMANTIC_LAYER_PATH = 'semantic_layer.yaml'

from typing import Optional

class QueryResult(BaseModel):
    is_ambiguous: bool = Field(description="True if the question is too vague and requires a clarification question.")
    clarification_question: Optional[str] = Field(description="If ambiguous, the question to ask the user to clarify. Otherwise null.")
    assumptions_made: list[str] = Field(description="List of assumptions made to generate the query.")
    sql: Optional[str] = Field(description="The SQLite query to answer the question, or null if the question cannot be answered.")
    explanation: Optional[str] = Field(description="A brief plain-English explanation of what the SQL query does.")

def load_semantic_layer():
    with open(SEMANTIC_LAYER_PATH, 'r') as file:
        return yaml.safe_load(file)

def execute_sql(sql: str) -> pd.DataFrame:
    """Executes SQL against the SQLite database and returns a pandas DataFrame."""
    logger.info(f"Executing SQL: {sql}")
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        logger.info(f"Execution successful. Rows returned: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        return pd.DataFrame({'error': [str(e)]})

def process_query(user_query: str) -> QueryResult:
    """Uses LLM to convert a natural language query into SQL."""
    logger.info(f"Processing new natural language query: '{user_query}'")
    semantic_layer = load_semantic_layer()
    schema_context = yaml.dump(semantic_layer, sort_keys=False)
    
    prompt = f"""
You are an expert AI SQL assistant. Your goal is to convert plain English questions into valid SQLite queries based on the provided semantic layer.

### SEMANTIC LAYER:
{schema_context}

### USER QUESTION:
{user_query}

### INSTRUCTIONS:
1. Carefully analyze the semantic layer to map synonyms and business terms to the correct tables and columns.
2. CRITICAL: If the user asks for a specific business metric (e.g., "revenue", "outstanding") that is defined in the `metrics` section of the semantic layer, you MUST use the EXACT SQL snippet provided in the configuration. Do not invent your own logic for these metrics.
3. If the user question is highly ambiguous (e.g., "top vendors" without specifying top by what), set 'is_ambiguous' to true and provide a 'clarification_question'.
4. If you make any reasonable assumptions (e.g., assuming "this year" means 2024), list them in 'assumptions_made'.
5. Generate the exact SQLite query to answer the question. Only use valid SQLite syntax.
6. Provide a simple, plain-English 'explanation' of the SQL query (e.g., "I joined invoices and vendors, filtered for paid invoices, and calculated the sum...").
"""

    logger.info("Sending prompt to OpenAI GPT-4o...")
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful text-to-SQL assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format=QueryResult,
    )
    
    result = response.choices[0].message.parsed
    if result.is_ambiguous:
        logger.info(f"Query deemed ambiguous. Clarification question: {result.clarification_question}")
    else:
        logger.info(f"Query successfully parsed into SQL. Assumptions made: {result.assumptions_made}")
        
    return result
