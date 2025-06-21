## Agent Instructions

This document provides specific instructions and conventions for AI agents working on the Deep Research Agent codebase.

1.  **Azure Credentials & Configuration:**
    *   The application relies on Azure OpenAI. Ensure that all interactions with `llm_handler.py` correctly use the configured Azure endpoint and deployment name.
    *   Authentication with Azure OpenAI **must** prioritize Azure Active Directory (AD) based methods (e.g., `DefaultAzureCredential` which can use service principals, managed identities, or CLI logins). API key usage might be present for simplicity in early development stages or placeholders but the goal is to use AD.
    *   Relevant environment variables for Azure configuration are detailed in `README.md`. Do not hardcode credentials.

2.  **Error Handling:**
    *   Implement robust error handling, especially for:
        *   API calls (PubMed, Azure OpenAI).
        *   File processing (PDF parsing).
        *   Configuration issues (missing environment variables).
    *   Provide informative messages to the user via the Streamlit interface when errors occur. Log detailed errors to the console for debugging.

3.  **Modularity and Code Structure:**
    *   Maintain the planned modular structure:
        *   `app.py`: Streamlit UI and main application flow.
        *   `utils/pdf_processor.py`: PDF content extraction.
        *   `utils/pubmed_fetcher.py`: PubMed API interactions.
        *   `utils/llm_handler.py`: Azure OpenAI LLM communication.
        *   `utils/research_agent.py`: Orchestration of research tasks, data aggregation, and prompt engineering.
    *   Avoid putting core logic directly into `app.py`; it should primarily handle UI and delegate tasks to the utility modules.

4.  **Pythonic Code and Readability:**
    *   Follow PEP 8 guidelines for Python code style.
    *   Use clear and descriptive variable and function names.
    *   Add comments to explain complex logic or non-obvious decisions.

5.  **Streamlit Usage:**
    *   Use Streamlit features effectively for building the user interface.
    *   Manage application state appropriately using Streamlit's mechanisms if needed (e.g., `st.session_state`).
    *   Ensure the UI is responsive and provides feedback to the user during long-running operations (e.g., API calls, LLM processing). Consider `st.spinner`.

6.  **PubMed API Interaction (`pubmed_fetcher.py`):**
    *   Be mindful of potential PubMed API rate limits. Implement respectful usage patterns (e.g., reasonable default for `max_results`).
    *   Use `Bio.Entrez` from Biopython if possible, as it's designed for NCBI APIs. Always set your email with `Entrez.email` as per NCBI guidelines.
    *   Focus on fetching abstracts. Full-text retrieval is complex due to paywalls and varying formats; if implemented, it must only target open-access articles.

7.  **LLM Interaction (`llm_handler.py` and `research_agent.py`):**
    *   **Prompt Engineering:** Construct clear, concise, and effective prompts for the LLM. The `research_agent.py` is primarily responsible for formulating these prompts by combining user queries with extracted text.
    *   **Context Management:** Be aware of LLM context window limitations. Implement strategies to handle large amounts of text (e.g., summarization, truncation, chunking if necessary, though initial implementation uses simple truncation).
    *   **Deployment Name:** The Azure OpenAI deployment name should be configurable (e.g., via an environment variable).

8.  **Dependencies:**
    *   Keep `requirements.txt` updated with all necessary packages.
    *   Specify versions if compatibility issues are known or anticipated, though for this project, flexible versions are initially acceptable.

9.  **Placeholder Code:**
    *   The initial setup includes placeholder functions. When implementing these, ensure they fulfill the documented purpose and integrate correctly with the rest of the application. Replace comments like `# TODO:` with actual implementations.

10. **Testing:**
    *   Thoroughly test changes manually by running the Streamlit application.
    *   Consider edge cases (e.g., no PDFs uploaded, PubMed query yields no results, API errors).
    *   Unit tests are encouraged for utility functions, especially those performing critical data transformations or API interactions.
```
