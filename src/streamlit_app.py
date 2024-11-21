import json
import base64
import requests
import pandas as pd
import streamlit as st

from cfg import Cfg

st.set_page_config(layout="wide")

url = f"http://{Cfg.app_host}:{Cfg.app_port}"

def send_request(endpoint: str, query_parameters=None, payload=None):
    request_url = url + endpoint
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if payload is not None:
        payload = json.dumps(payload)
    response = requests.post(url=request_url, params=query_parameters, data=payload, headers=headers)
    return response.text

def main():
    # Remove whitespace from the top of the page and sidebar
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 2.5rem;
                    padding-bottom: 5rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("PDF Q/A")

    col1, col2 = st.columns([1, 1], vertical_alignment="center")

    with col1:
        document = st.file_uploader("Upload document", type=["pdf"])

    with col2:
        df = pd.DataFrame(columns=["Question"])
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        queries = edited_df['Question'].to_list()

    if st.button("Process Document", use_container_width=True):
        if document is not None and len(queries) > 0:
            with st.status("Processing query...", expanded=False):
                st.write("Parsing data...")
                response = send_request(endpoint="/parse", payload={"document": base64.b64encode(document.read()).decode('latin-1')})
                extracted_text = json.loads(response)["extracted_text"]
                
                st.write("Chunking the data...")
                response = send_request(endpoint="/chunking", payload={"document": extracted_text})
                text_list = json.loads(response)["text_list"]

                st.write("Ingesting data...")
                send_request(endpoint="/vector_db/create_collection")
                send_request(endpoint="/vector_db/insert_bulk", payload={"data": text_list})

                st.write("Getting answers...")
                response = send_request(endpoint="/document_chat", payload={"questions": queries})
                response = json.loads(response)
            
            st.json(response)
        else:
            st.error("Please upload a document and provide questions.")
    
if __name__ == "__main__":
    main()
