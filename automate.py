import streamlit as st 

st.set_page_config(page_title="RAG with Local DeepSeek R1")

import os
import chromadb
chromadb.config.disable_telemetry = True

import tempfile
import time
from streamlit_chat import message
from rag import ChatPDF
from langchain_community.vectorstores import Chroma

from chromadb.config import Settings

chroma_settings = Settings(anonymized_telemetry=False, is_persistent=True)
from datetime import datetime 
import glob

def display_messages():
    """Display the chat history."""
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        st.subheader("Chat History")
        for i, (msg, is_user) in enumerate(st.session_state["messages"]):
            message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    """Process the user input and generate an assistant response."""
    if "user_input" in st.session_state and st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking..."):
            try:
                # Check if vector store exists before asking the assistant
                if not hasattr(st.session_state["assistant"], "vector_store"):
                    st.session_state["messages"].append(("Vector store not found. Please upload a document.", False))
                    return
                
                agent_text = st.session_state["assistant"].ask(
                    user_text,
                    k=st.session_state["retrieval_k"],
                    score_threshold=st.session_state["retrieval_threshold"],
                )
            except ValueError as e:
                agent_text = str(e)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))

def read_and_save_file():
    """Handle file upload and ingestion."""
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        # Create a progress bar widget
        progress_bar = st.progress(0)
        total_steps = 100  # You can adjust this based on the size of the file or tasks

        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}..."):
            t0 = time.time()

            # Ingest the PDF file and ensure it's saved in the vector store
            try:
                st.session_state["assistant"].ingest(file_path)
                # Force the vector store to save after ingestion (if applicable)
                if hasattr(st.session_state["assistant"], "vector_store"):
                    st.session_state["assistant"].vector_store.persist()
                    st.session_state["messages"].append(("Vector store saved after ingestion.", False))
                else:
                    st.session_state["messages"].append(("No vector store found after ingestion.", False))
            except Exception as e:
                st.session_state["messages"].append((f"Error during ingestion: {str(e)}", False))

            # Update progress bar (simulate, replace with actual progress logic)
            for step in range(total_steps):
                time.sleep(0.1)  # Simulate work done by updating progress
                progress_bar.progress((step + 1) / total_steps)

            t1 = time.time()

        # Notify user of ingestion success
        st.session_state["messages"].append(
            (f"Ingested {file.name} in {t1 - t0:.2f} seconds", False)
        )
        os.remove(file_path)

        # Check if the vector store is being saved/created
        if hasattr(st.session_state["assistant"], "vector_store"):
            st.session_state["messages"].append(
                ("Vector store has been created successfully.", False)
            )
        else:
            st.session_state["messages"].append(
                ("No vector store found after ingestion.", False)
            )


def load_vector_store():
    """Load the vector store from disk if it exists."""
    vector_store_path = "chroma_db"
    if os.path.exists(vector_store_path):  # Check if the chroma_db directory exists
        st.session_state["assistant"].vector_store = Chroma(
            persist_directory=vector_store_path, 
            embedding_function=st.session_state["assistant"].embeddings,
            client_settings=chroma_settings,
        )
        st.session_state["messages"].append(("Loaded persisted vector store.", False))
    else:
        st.session_state["messages"].append(("No vector store found at the specified path.", False))

def get_files_matching_pattern(directory, pattern):
    search_path = os.path.join(directory, pattern)
    files = glob.glob(search_path)
    return sorted(files)

def mass_process():
    caseDir = r"C:\rag\chatpdf-rag-deepseek-r1\cases"
    st.write("Case dir: " + caseDir)
    file_pattern = "*.txt"
    matching_files = get_files_matching_pattern(caseDir, file_pattern)
    
    time1 = datetime.now()
    formatted = time1.strftime("%Y_%m_%d_%H_%M_%S")
    
    if matching_files:
        st.write("Txt files found, prepare to process")
    else:
        st.write("No txt files found, double check the folder " + caseDir)
        return;
    
    for txtpath in matching_files:
        #txtpath = os.path.join(caseDir, filename)
        #outpath = os.path.join(caseDir, filename + "." + formatted + ".out")
        outpath = txtpath + "." + formatted + ".out"
        try:            
            with open(txtpath, 'r', encoding='UTF8') as f:
                content = f.read()
                content = content.strip()
                if len(content) > 0:
                    st.write("Process file " + txtpath)
                    #st.write(content)
                    process_one_file(content, outpath)
                else:
                    st.write("file " + txtpath + " is empty")
                
        except Exception as e:
            st.write(f"Error processing {txtpath}: {e}")

def process_one_file(content, outpath):
    with st.session_state["thinking_spinner"], st.spinner("Thinking..."):
        try:
            if not hasattr(st.session_state["assistant"], "vector_store"):
                st.session_state["messages"].append(("Vector store not found. Please upload a document.", False))
                return
                
            agent_text = st.session_state["assistant"].ask(content, k=st.session_state["retrieval_k"], score_threshold=st.session_state["retrieval_threshold"],)
            with open(outpath, 'w', encoding='UTF8') as f:
                f.write("Input=================>\n")
                f.write(content)
                f.write("\n\n")
                f.write("Output=================>\n")
                f.write(agent_text)
                f.write("\n")
        
        except ValueError as e:
             st.write(f"Error processing {outpath}: {e}")
            
               
def page():
    """Main app page layout."""

    # Initialize session state variables if not already initialized
    if "assistant" not in st.session_state:
        st.session_state["assistant"] = ChatPDF()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""

    if "ingestion_spinner" not in st.session_state:
        st.session_state["ingestion_spinner"] = st.empty()

    # Load vector store when the app starts
    load_vector_store()

    # Display the app header
    st.header("RAG with Local DeepSeek R1")

    # Upload document section
    st.subheader("Upload a Document")
    st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    # Add button to check vector store status with unique key
    if st.button("Check Vector Store Status", key="check_vector_store_status"):
        if hasattr(st.session_state["assistant"], "vector_store") and st.session_state["assistant"].vector_store is not None:
            st.write("Vector store is loaded successfully.")
        else:
            st.write("No vector store found.")
            
    st.subheader("click on the button below to start mass processing")
    if st.button("Start mass processing", key="start_mass_processing"):
        time1 = datetime.now()
        formatted = time1.strftime("%Y-%m-%d %H:%M:%S")
        st.write("starting process at " + formatted)
        mass_process()
        time2 = datetime.now()
        formatted = time2.strftime("%Y-%m-%d %H:%M:%S")
        st.write("Finish process at " + formatted)
        diff = time2 - time1
        st.write(f"Time difference: {diff} seconds")
        
    
    st.session_state["ingestion_spinner"] = st.empty()

    # Retrieval settings
    st.subheader("Settings")
    st.session_state["retrieval_k"] = st.slider(
        "Number of Retrieved Results (k)", min_value=1, max_value=10, value=5
    )
    st.session_state["retrieval_threshold"] = st.slider(
        "Similarity Score Threshold", min_value=0.0, max_value=1.0, value=0.2, step=0.05
    )

    # Display messages and text input
    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

    # Clear chat button with unique key
    if st.button("Clear Chat", key="clear_chat_button"):
        st.session_state["messages"] = []
        st.session_state["user_input"] = ""
        #st.session_state["assistant"].clear()
        st.session_state["assistant"].clear_chat_only()
        

if __name__ == "__main__":
    page()
