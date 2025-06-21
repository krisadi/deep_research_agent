# Deep Q&A Research Agent

This application is an advanced research assistant that answers user questions by synthesizing information from multiple sources. It leverages Large Language Models (LLMs) via Azure OpenAI for its core reasoning capabilities.

## Features

-   **Multi-Source Data Ingestion:**
    -   **PubMed Articles:** Fetches abstracts from PubMed.
    -   **DuckDuckGo Search:** Retrieves web search snippets.
    -   **PDF Document Processing (Text-Based PDFs):**
        -   Extracts text directly from digital, text-based PDF documents. (OCR for image-based PDFs is NOT supported).
        -   Chunks processed PDF text.
        -   Indexes these chunks into an in-memory FAISS vector store using sentence embeddings (via Sentence Transformers).
        -   Retrieves relevant PDF chunks based on semantic similarity to the user's query.
-   **Azure OpenAI Integration:** Uses an LLM (via Azure OpenAI) to synthesize information from all gathered sources and answer the user's research question.
-   **Streamlit UI:**
    -   Allows users to input a research question.
    -   Select data sources (PubMed, DuckDuckGo, Indexed PDFs).
    -   Upload PDF files for indexing and searching.
    -   Displays a log of the research process and the final synthesized answer.
-   **Modular Design:** Code is organized into utility modules for search, PDF indexing, vector store management, and LLM interaction.

## Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url> # Replace with your repo URL
cd <your-repository-directory> # Replace with your repo directory name
```

### 2. Create and Activate a Virtual Environment
It's highly recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```
This includes libraries like Streamlit, Langchain, FAISS, PyPDF2, DuckDuckGo-Search, OpenAI, Azure-Identity, etc. OCR-related Python libraries (`pytesseract`, `pdf2image`, `Pillow` for OCR purposes) are no longer required.

### 4. Configure Environment Variables

It's recommended to create a `.env` file in the project root directory and list your environment variables there. Add `python-dotenv` to your `requirements.txt` and load it in `app.py` if you want automatic loading from `.env`. Alternatively, export these variables in your shell.

Required variables:

*   **Azure OpenAI Credentials:**
    *   `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI resource endpoint.
    *   `AZURE_OPENAI_DEPLOYMENT_NAME`: The name of your chat model deployment (e.g., gpt-35-turbo).
    *   `AZURE_OPENAI_API_VERSION`: (Optional, defaults in `utils/llm_handler.py`) e.g., "2024-02-15-preview".
    *   For Azure AD Authentication (recommended, used by `DefaultAzureCredential`):
        *   If using a Service Principal: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.
        *   Alternatively, for local development, ensure you are logged in via Azure CLI (`az login`).
        *   If deploying on Azure services (like App Service, VMs), a Managed Identity can be used.
        *   The identity being used needs the "Cognitive Services OpenAI User" role (or similar with data plane access) assigned on your Azure OpenAI resource.

*   **NCBI Email (for PubMed Access):**
    Set this for respectful use of the NCBI Entrez API.
    `NCBI_EMAIL="your.email@example.com"` (replace with your actual email).

Example `.env` file content:
```env
AZURE_OPENAI_ENDPOINT="https://YOUR_RESOURCE_NAME.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="YOUR_DEPLOYMENT_NAME"
# AZURE_CLIENT_ID="YOUR_SP_CLIENT_ID" # If using Service Principal
# AZURE_TENANT_ID="YOUR_AZURE_TENANT_ID" # If using Service Principal
# AZURE_CLIENT_SECRET="YOUR_SP_CLIENT_SECRET" # If using Service Principal
NCBI_EMAIL="your.email@example.com"
```
If you use a `.env` file, you would add `from dotenv import load_dotenv; load_dotenv()` at the beginning of `app.py` and add `python-dotenv` to `requirements.txt`. For now, the README assumes manual export or direct setting if `.env` isn't explicitly loaded by the app.

## Running the Application
Once all dependencies are installed and environment variables are configured:
```bash
streamlit run app.py
```
Access the application in your web browser, typically at `http://localhost:8501`.

## Usage
1.  **Enter Research Question:** Type your question in the sidebar.
2.  **Select Data Sources:** Choose from "PubMed Articles", "DuckDuckGo Search", and "Indexed PDFs".
3.  **Upload PDFs (Optional):** If "Indexed PDFs" is selected, upload relevant **text-based digital** PDF files. They will be processed and indexed for semantic search for the current session.
4.  **Start Research:** Click the "Start Research" button.
5.  **View Results:** The agent will fetch data from selected sources, process PDFs, query the LLM, and display a synthesized answer. A log of actions is also shown.

## Project Structure
-   `app.py`: Main Streamlit application file.
-   `utils/`: Directory for helper modules.
    -   `research_agent.py`: Core orchestration logic for the research process.
    -   `llm_handler.py`: Handles communication with Azure OpenAI.
    -   `pubmed_fetcher.py`: Interacts with the PubMed API.
    -   `duckduckgo_searcher.py`: Interface for DuckDuckGo search.
    -   `document_indexer.py`: Handles PDF text extraction (from text-based PDFs) and chunking.
    -   `vector_store_handler.py`: Manages the FAISS vector store and similarity searches.
-   `requirements.txt`: Python dependencies.
-   `README.md`: This file.
-   `AGENTS.md`: Specific instructions for AI development agents working on this codebase.

```
