import streamlit as st
from dotenv import load_dotenv # For loading .env file
from utils import research_agent # research_agent will import its dependencies
from utils.research_agent import SOURCE_PDF, SOURCE_PUBMED, SOURCE_DUCKDUCKGO # Import constants
from typing import Set
import os # For environment variable checks

# Load environment variables from .env file at the very beginning
load_dotenv()

# --- Default Credentials (INSECURE - FOR DEMO/LOCAL USE ONLY) ---
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password" # Replace with something slightly less obvious if you must

# Attempt to import from streamlit_extras - currently not used actively for copy button
try:
    # from streamlit_extras.streaming_write import write as streaming_write # Example import
    # from streamlit_extras.echo_expander import echo_expander # Example import
    streamlit_extras_available = True 
except ImportError:
    streamlit_extras_available = False
    # This warning can be shown once, maybe not on every run if login is implemented.
    # st.warning("`streamlit-extras` not fully available. Some UI features might be basic or unavailable.")

def show_login_form():
    """Displays the login form and handles login logic."""
    st.subheader("Login Required")
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.login_error = "" # Clear any previous error
                st.experimental_rerun() # Rerun to show main app
            else:
                st.session_state.login_error = "Invalid username or password."
    
    if "login_error" in st.session_state and st.session_state.login_error:
        st.error(st.session_state.login_error)


def display_main_app():
    """Displays the main research agent application UI."""
    st.title("📚 Deep Q&A Research Agent")
    st.markdown("""
    Ask your research question, select your data sources, and let the agent synthesize information for you.
    The agent can use PubMed articles, DuckDuckGo search results, and insights from your uploaded (and indexed) PDF documents.
    It leverages Azure OpenAI for analysis and synthesis.
    """)

    # Initialize session state variables for the main app (if not already set by login)
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results' not in st.session_state:
        st.session_state.results = ""
    if 'progress_messages' not in st.session_state:
        st.session_state.progress_messages = []
    # pdf_indexed_this_session is not used in this version, vector store is per-run

    # --- Sidebar Controls ---
    st.sidebar.header("⚙️ Query Configuration")
    
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.login_error = "" # Clear login error on logout
        # Clear other session data if needed upon logout
        st.session_state.results = ""
        st.session_state.progress_messages = []
        st.experimental_rerun()

    query = st.sidebar.text_input("Enter your research question:", 
                                  help="Your main research question. This will be used for all selected data sources.")
    
    available_sources = [SOURCE_PUBMED, SOURCE_DUCKDUCKGO, SOURCE_PDF]
    default_sources = [SOURCE_PUBMED, SOURCE_DUCKDUCKGO] 

    selected_sources: Set[str] = set(st.sidebar.multiselect(
        "Select Data Sources:",
        options=available_sources,
        default=default_sources,
        help="Choose the information sources to query. 'Indexed PDFs' requires you to upload PDFs."
    ))

    uploaded_files = None
    if SOURCE_PDF in available_sources: 
        uploaded_files = st.sidebar.file_uploader(
            "Upload PDF files (for 'Indexed PDFs' source):", 
            accept_multiple_files=True, 
            type="pdf",
            help="Upload PDF documents if you've selected 'Indexed PDFs' as a source. These will be processed for semantic search."
        )
        if uploaded_files and SOURCE_PDF in selected_sources:
            st.sidebar.info(f"{len(uploaded_files)} PDF(s) ready for processing if 'Indexed PDFs' is run.")
        elif not uploaded_files and SOURCE_PDF in selected_sources:
            st.sidebar.warning("Please upload PDF files if you intend to use the 'Indexed PDFs' source.")

    if SOURCE_PUBMED in selected_sources:
        st.sidebar.subheader(f"{SOURCE_PUBMED} Options")
        max_pubmed_articles = st.sidebar.slider("Max PubMed Articles:", 
                                                min_value=1, max_value=10, value=3,
                                                help="Number of relevant PubMed article abstracts to fetch.")
    else:
        max_pubmed_articles = 0

    start_button = st.sidebar.button("🚀 Start Research", disabled=st.session_state.processing, type="primary")
    st.sidebar.markdown("---")

    # Proactive warnings for essential configurations
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    ncbi_email = os.getenv("NCBI_EMAIL")

    if not azure_endpoint:
        st.sidebar.warning("⚠️ AZURE_OPENAI_ENDPOINT is not set. LLM features will be unavailable.")
    
    if not ncbi_email or ncbi_email == "your_email@example.com":
        st.sidebar.warning("⚠️ NCBI_EMAIL is not set or uses a placeholder. PubMed searches may be less reliable.")

    st.sidebar.caption("Ensure Azure OpenAI and NCBI_EMAIL environment variables are correctly set as per the README.")

    # --- Main Page Layout ---
    log_col, results_col = st.columns([1, 2]) 

    with log_col:
        st.subheader("📝 Research Process Log")
        progress_placeholder = st.empty() 

    with results_col:
        st.subheader("💡 Synthesized Answer & Findings")
        results_display_area = st.empty() 

    # --- Research Logic Trigger ---
    if start_button:
        if not query.strip():
            st.sidebar.error("⚠️ Please enter a research question.")
        elif not selected_sources:
            st.sidebar.error("⚠️ Please select at least one data source.")
        elif SOURCE_PDF in selected_sources and not uploaded_files:
            st.sidebar.error(f"⚠️ '{SOURCE_PDF}' is selected, but no PDF files were uploaded.")
        else:
            st.session_state.processing = True
            st.session_state.results = "" 
            st.session_state.progress_messages = [] 
            
            def streamlit_progress_update(message: str):
                st.session_state.progress_messages.append(message)

            with st.spinner("🧠 Performing research... Please wait."):
                try:
                    report = research_agent.conduct_research(
                        query=query,
                        selected_data_sources=selected_sources,
                        uploaded_pdf_files=uploaded_files if SOURCE_PDF in selected_sources else None,
                        max_pubmed_articles=max_pubmed_articles if SOURCE_PUBMED in selected_sources else 0,
                        on_progress_update=streamlit_progress_update
                    )
                    st.session_state.results = report
                except Exception as e:
                    st.session_state.results = f"An unexpected critical error occurred: {str(e)}"
                    st.session_state.progress_messages.append(f"CRITICAL ERROR: {str(e)}")
                    st.error(f"Critical error during research: {str(e)}") 
                finally:
                    st.session_state.processing = False
                    st.experimental_rerun() 

    # --- Displaying Progress and Results ---
    if st.session_state.progress_messages:
        progress_placeholder.text_area("Log:", "".join([f"- {msg}\n" for msg in st.session_state.progress_messages]), height=400, disabled=True)
    else:
        progress_placeholder.info("Research log will appear here once processing starts.")

    if st.session_state.results:
        results_display_area.markdown(st.session_state.results, unsafe_allow_html=True)
        results_display_area.markdown("*(To copy the report, please select the text and use Ctrl+C or Cmd+C.)*", unsafe_allow_html=True)
    else:
        results_display_area.info("Research findings will appear here.")


def main():
    st.set_page_config(layout="wide", page_title="Deep Q&A Research Agent")

    # Initialize login state if not present
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_error" not in st.session_state: # To store login error messages
        st.session_state.login_error = ""


    if st.session_state.logged_in:
        display_main_app()
    else:
        show_login_form()

if __name__ == "__main__":
    main()
