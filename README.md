# Local RAG with DeepSeek R1

Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and generate responses based on given sources.

## Features

- **PDF Upload**: Upload one or more PDF documents to enable question-answering across their combined content.
- **RAG Workflow**: Combines retrieval and generation for high-quality responses.
- **Customizable Retrieval**: Adjust the number of retrieved results (`k`) and similarity threshold to fine-tune performance.
- **Memory Management**: Easily clear vector store and retrievers to reset the system.
- **Streamlit Interface**: A user-friendly web application for seamless interaction.

---

## Installation

Follow the steps below to set up and run the application:

### 1. Clone the Repository

```bash
git clone https://github.com/u0974250-ai/rag-chatpdf-app
cd rag-chatpdf-app
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

```Windows Powershell
python -m venv venv
set-executionpolicy remotesigned -scope process
.\venv\Scripts\activate.ps1
```

### 3. Install Dependencies

Install the required Python packages:

```bash or Windows Powershell
pip install -r requirements.txt
```

Make sure to include the following packages in your `requirements.txt`:

```
streamlit
langchain
langchain_ollama
langchain_community
streamlit-chat
pypdf
chromadb
```

### 4. Pull Required Models for Ollama

To use the specified embedding and LLM models (`mxbai-embed-large` and `deepseek-r1`), download them via the `ollama` CLI:

```bash or Windows Powershell
ollama pull mxbai-embed-large
ollama pull deepseek-r1:latest
```

---

## Usage

### 1. Start the Application

Run the Streamlit app:

```bash or Windows Powershell
streamlit run automate.py
```

- In automate.py, def mass_process(), modify the case folder (**caseDir**) according to your setup. 

### 2. Upload Documents

- Navigate to the **Upload a Document** section in the web interface.
- Upload one or multiple PDF files to process their content.
- Each file will be ingested automatically and confirmation messages will show processing time.

### 3.1 Ask Questions

- Type your question in the chat input box and press Enter.
- Adjust retrieval settings (`k` and similarity threshold) in the **Settings** section for responses tailored to your purposes.

### 3.2 Clear Chat

- Use the **Clear Chat** button to reset the chat interface.
- Clearing the chat DOES NOT reset the vector store and retriever.

### 4.1 Mass process cases

- Copy all case files into the case folder. One text file (with extension of '.txt') represents one case.
- Use the **Start mass processing** button to process all cases within the 'case' folder.
- After processing has finished, the answers will be written to .out files, and timestamped.

### 5 To reset

- To reset, simply shutdown streamlit.
- If you want to clear your vector store, delete the chroma_db folder.

---

## Project Structure

```
.
├── rag.py                  # Core RAG logic for PDF ingestion and question-answering
├── requirements.txt        # List of required Python dependencies
├── automate.py             # Streamlit app for the user interface and automatically running cases 
├── chroma_db/              # Local persistent vector store (auto-generated)
├── cases/                  # Store of cases for automate.py
└── README.md               # Project documentation
```

---

## Configuration

You can modify the following parameters in `rag.py` to suit your needs:

1. **Models**:
   - Default LLM: `deepseek-r1:latest` (7B parameters)
   - Default Embedding: `mxbai-embed-large` (1024 dimensions)
   - Change these in the `ChatPDF` class constructor or when initializing the class
   - Any Ollama-compatible model can be used by updating the `llm_model` parameter

2. **Chunking Parameters**:
   - `chunk_size=1024` and `chunk_overlap=100`
   - Adjust for larger or smaller document splits

3. **Retrieval Settings**:
   - Adjust `k` (number of retrieved results) and `score_threshold` in `ask()` to control the quality of retrieval.

---

## Requirements

- **Python**: 3.8+
- **Streamlit**: Web framework for the user interface.
- **Ollama**: For embedding and LLM models.
- **LangChain**: Core framework for RAG.
- **PyPDF**: For PDF document processing.
- **ChromaDB**: Vector store for document embeddings.

---

## Troubleshooting

### Common Issues

1. **Missing Models**:
   - Ensure you've pulled the required models using `ollama pull`.

2. **Vector Store Errors**:
   - Delete the `chroma_db/` directory if you encounter dimensionality errors:
     ```bash
     rm -rf chroma_db/
     ```
   - To digest new documents/clear vector store, delete chroma_db folder and upload new docs.

3. **Streamlit Not Launching**:
   - Verify dependencies are installed correctly using `pip install -r requirements.txt`.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments & Credits

- [LangChain](https://github.com/hwchase17/langchain)
- [Streamlit](https://github.com/streamlit/streamlit)
- [Ollama](https://ollama.ai/)
- This project is based on [chatpdf-rag-deepseek-r1](https://github.com/paquino11/chatpdf-rag-deepseek-r1) by [Pedro Aquino]. 