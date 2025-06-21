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

This project uses a `.env` file to manage environment variables. The application will automatically load variables from a file named `.env` located in the project root directory at startup.

**Steps to Configure:**

1.  **Create a `.env` file:**
    Copy the provided template file `.env.example` to a new file named `.env` in the project root:
    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env`:**
    Open the newly created `.env` file and fill in your actual credentials and configuration values. **Do not commit the `.env` file to version control.** It should contain your secrets.

3.  **`.gitignore`:**
    The `.gitignore` file in this project is already configured to ignore `.env` files, ensuring your secrets are not accidentally committed.

**Required Variables (to be set in your `.env` file):**

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
    `NCBI_EMAIL="your_actual_email@example.com"` (replace with your actual email).

*   **Specialized Model Settings (o3-mini):**
    *   The application automatically applies specialized settings if your `AZURE_OPENAI_DEPLOYMENT_NAME` (set in `.env`) includes "o3-mini". See `.env.example` for details.

The `.env.example` file provides a template for all these variables.

## Running the Application
Once all dependencies are installed and environment variables are configured:
```bash
streamlit run app.py
```
Access the application in your web browser, typically at `http://localhost:8501`.

## Usage

### Logging In
The application now features a simple login page to control access.
-   **Default Username:** `admin`
-   **Default Password:** `password` (Note: This is defined in `app.py` and can be changed there.)

**Important Security Note:** These default credentials are hardcoded and are **highly insecure**. This login mechanism is intended for basic local development or demo purposes only and should **not** be used in a production or sensitive environment without implementing a proper, secure authentication system.

### Performing Research
Once logged in:
1.  **Enter Research Question:** Type your question in the sidebar.
2.  **Select Data Sources:** Choose from "PubMed Articles", "DuckDuckGo Search", and "Indexed PDFs".
3.  **Upload PDFs (Optional):** If "Indexed PDFs" is selected, upload relevant **text-based digital** PDF files. They will be processed and indexed for semantic search for the current session.
4.  **Start Research:** Click the "Start Research" button.
5.  **View Results:** The agent will fetch data from selected sources, process PDFs, query the LLM, and display a synthesized answer. A log of actions is also shown.
6.  **Logout:** A logout button is available in the sidebar.

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