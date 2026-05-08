import streamlit as st
import pandas as pd
from query_engine import process_query, execute_sql

st.set_page_config(page_title="Cashflo Data Assistant", page_icon="💡", layout="wide")

# Custom CSS for a better UI
st.markdown("""
<style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .user-msg {
        background-color: #2b313e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .assistant-msg {
        background-color: #1e232d;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #4CAF50;
    }
    .ambiguous-msg {
        background-color: #3b2e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #FF9800;
    }
</style>
""", unsafe_allow_html=True)

st.title("💡 Cashflo NLP-to-SQL Assistant")
st.markdown("Ask natural language questions about your Accounts Payable data.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        if msg.get("is_ambiguous"):
             st.markdown(f'<div class="ambiguous-msg"><b>Assistant:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
             st.markdown(f'<div class="assistant-msg"><b>Assistant:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        
        # Display assumptions if any
        if msg.get("assumptions"):
            with st.expander("Assumptions Made"):
                for a in msg["assumptions"]:
                    st.write(f"- {a}")
        
        # Display SQL and Data
        if msg.get("sql"):
            with st.expander("View SQL Query"):
                st.code(msg["sql"], language="sql")
            
            if "data" in msg and not msg["data"].empty:
                st.dataframe(msg["data"], width="stretch")
            elif "data" in msg and msg["data"].empty:
                st.info("Query executed successfully but returned no results.")

# Chat input
if prompt := st.chat_input("E.g., What was our total invoice amount from Mumbai vendors last quarter?"):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-msg"><b>You:</b> {prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Analyzing your question..."):
        try:
            # Call our query engine
            result = process_query(prompt)
            
            assistant_response = {
                "role": "assistant",
                "content": result.explanation if result.explanation else "Here are the results.",
                "is_ambiguous": result.is_ambiguous,
                "assumptions": result.assumptions_made,
                "sql": result.sql,
                "data": pd.DataFrame()
            }
            
            if result.is_ambiguous and result.clarification_question:
                assistant_response["content"] = result.clarification_question
            
            if result.sql and not result.is_ambiguous:
                # Execute the SQL
                df = execute_sql(result.sql)
                assistant_response["data"] = df
                
                if 'error' in df.columns:
                    assistant_response["content"] = f"Error executing query: {df['error'].iloc[0]}"
            
            st.session_state.messages.append(assistant_response)
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
