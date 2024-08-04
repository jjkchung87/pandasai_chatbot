from pandasai.llm.local_llm import LocalLLM
import streamlit as st
from pandasai.connectors import PostgreSQLConnector
from pandasai import SmartDataframe
import requests
import json

# Function to check if the Local LLM server is reachable
def check_server_reachability():
    try:
        response = requests.get("http://localhost:11434")
        if response.status_code != 200:
            return False, f"LLM server is not reachable: {response.status_code}"
        else:
            return True, "LLM server is reachable"
    except requests.exceptions.RequestException as e:
        return False, f"Error connecting to LLM server: {e}"

# Check server reachability
reachable, message = check_server_reachability()
if not reachable:
    st.error(message)
else:
    st.write(message)

# Define the LocalLLM object
llm = LocalLLM(
    api_base="http://localhost:11434/v1",
    model="llama3"
)

st.title("PandasAI Local LLM Demo")

# Create a PostgreSQLConnector object
connector = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "marketingplanner",
        "username": "justinchung",
        "password": "password",
        "table": "campaigns"
    }
)

# Allow pandas import by updating the whitelist
whitelist = ["pandas", "matplotlib"]

# Create a SmartDataframe object with the updated whitelist
df_connector = SmartDataframe(connector, config={"llm": llm, "whitelist": whitelist})

# Test API call
st.write("Testing API call:")
test_payload = {
    "model": "llama3.1",
    "prompt": "Hello"
}
try:
    response = requests.post("http://localhost:11434/v1/completions", headers={"Content-Type": "application/json"}, data=json.dumps(test_payload))
    st.write(f"Test API call status: {response.status_code}")
    st.write(f"Test API call response: {response.text}")
except requests.exceptions.RequestException as e:
    st.error(f"Error in test API call: {e}")

prompt = st.text_input("Enter a prompt")

if st.button("Submit"):
    if prompt:
        with st.spinner("Loading..."):
            try:
                generated_code = df_connector.chat(prompt)
                st.write("Generated Code:")
                st.code(generated_code)
                
                # Ensure the generated code doesn't contain malicious functions
                safe_functions = ["pd", "plt", "numpy", "np"]
                if any(func in generated_code for func in safe_functions):
                    st.write(df_connector.chat(prompt))
                else:
                    st.error("The generated code contains potentially unsafe functions.")
            except Exception as e:
                st.error(f"Error: {e}")