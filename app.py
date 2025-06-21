import streamlit as st
from utils import research_agent # research_agent will import its dependencies
from utils.research_agent import SOURCE_PDF, SOURCE_PUBMED, SOURCE_DUCKDUCKGO # Import constants
from typing import Set

# Attempt to import copy_to_clipboard from streamlit_extras
try:
    from streamlit_extras.streaming_write import write as streaming_write
    from streamlit_extras.echo_expander import echo_expander
    # For copy button, streamlit_extras has stx.copy_button but let's try a more direct one if available or build simply
    # For now, we'll use a basic JS approach if streamlit_extras doesn't have an easy copy button.
    # A common one is `st_copy_to_clipboard` but it was in a different extras package.
    # Let's try a placeholder for copy button logic first.
    streamlit_extras_available = True
except ImportError:
    streamlit_extras_available = False
    st.warning("`streamlit-extras` not fully available. Some UI features like 'Copy to Clipboard' might be basic or unavailable. Install with `pip install streamlit-extras`")

def main():
    st.set_page_config(layout="wide", page_title="Deep Q&A Research Agent")
    st.title("📚 Deep Q&A Research Agent")
    st.markdown("""
    Ask your research question, select your data sources, and let the agent synthesize information for you.
    The agent can use PubMed articles, DuckDuckGo search results, and insights from your uploaded (and indexed) PDF documents.
    It leverages Azure OpenAI for analysis and synthesis.
    """)

    # Initialize session state variables
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results' not in st.session_state:
        st.session_state.results = ""
    if 'progress_messages' not in st.session_state:
        st.session_state.progress_messages = []
    if 'pdf_indexed_this_session' not in st.session_state:
        st.session_state.pdf_indexed_this_session = False # To track if indexing has happened

    # --- Sidebar Controls ---
    st.sidebar.header("⚙️ Query Configuration")
    query = st.sidebar.text_input("Enter your research question:", 
                                  help="Your main research question. This will be used for all selected data sources.")
    
    available_sources = [SOURCE_PUBMED, SOURCE_DUCKDUCKGO, SOURCE_PDF]
    # Ensure PubMed is pre-selected and handled as "mandatory" if needed.
    # For this iteration, we make it pre-selected. User can deselect if they wish.
    default_sources = [SOURCE_PUBMED, SOURCE_DUCKDUCKGO] 

    selected_sources: Set[str] = set(st.sidebar.multiselect(
        "Select Data Sources:",
        options=available_sources,
        default=default_sources,
        help="Choose the information sources to query. 'Indexed PDFs' requires you to upload PDFs."
    ))

    # PDF Upload - only show if PDF source is potentially selectable or selected
    uploaded_files = None
    if SOURCE_PDF in available_sources: # Always show uploader if it's an option
        uploaded_files = st.sidebar.file_uploader(
            "Upload PDF files (for 'Indexed PDFs' source):", 
            accept_multiple_files=True, 
            type="pdf",
            help="Upload PDF documents if you've selected 'Indexed PDFs' as a source. These will be OCRed and indexed for semantic search."
        )
        if uploaded_files and SOURCE_PDF in selected_sources:
            st.sidebar.info(f"{len(uploaded_files)} PDF(s) ready for indexing/searching if 'Indexed PDFs' is run.")
        elif not uploaded_files and SOURCE_PDF in selected_sources:
            st.sidebar.warning("Please upload PDF files if you intend to use the 'Indexed PDFs' source.")


    # Source-specific controls
    if SOURCE_PUBMED in selected_sources:
        st.sidebar.subheader(f"{SOURCE_PUBMED} Options")
        max_pubmed_articles = st.sidebar.slider("Max PubMed Articles:", 
                                                min_value=1, max_value=10, value=3,
                                                help="Number of relevant PubMed article abstracts to fetch.")
    else:
        max_pubmed_articles = 0 # Default if not selected

    # DuckDuckGo results are fixed by a constant in research_agent for now.
    # Could add a slider for MAX_DUCKDUCKGO_RESULTS if desired.

    start_button = st.sidebar.button("🚀 Start Research", disabled=st.session_state.processing, type="primary")
    st.sidebar.markdown("---")


    # --- Main Page Layout ---
    log_col, results_col = st.columns([1, 2]) # Log on left, results on right

    with log_col:
        st.subheader("📝 Research Process Log")
        progress_placeholder = st.empty() # For dynamic updates of the log list

    with results_col:
        st.subheader("💡 Synthesized Answer & Findings")
        results_display_area = st.empty() # For displaying the final report

    # --- Research Logic Trigger ---
    if start_button:
        if not query.strip():
            st.sidebar.error("⚠️ Please enter a research question.")
        elif not selected_sources:
            st.sidebar.error("⚠️ Please select at least one data source.")
        elif SOURCE_PDF in selected_sources and not uploaded_files:
            st.sidebar.error(f"⚠️ '{SOURCE_PDF}' is selected, but no PDF files were uploaded. Please upload PDFs or deselect this source.")
        else:
            st.session_state.processing = True
            st.session_state.results = "" # Clear previous results
            st.session_state.progress_messages = [] # Clear previous log
            
            # This flag might be more complex if we want to preserve index across non-PDF related runs
            st.session_state.pdf_indexed_this_session = (SOURCE_PDF in selected_sources and uploaded_files is not None)

            def streamlit_progress_update(message: str):
                st.session_state.progress_messages.append(message)
                # Update the placeholder with new messages (basic approach)
                # A more robust live log might use st.container() and add st.text to it.
                # For now, we'll update the full list.

            with st.spinner("🧠 Performing research... This may involve fetching data, OCR, indexing, and LLM synthesis. Please wait."):
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
                    st.error(f"Critical error during research: {str(e)}") # Show prominent error
                finally:
                    st.session_state.processing = False
                    st.experimental_rerun() # Rerun to update UI state cleanly after processing

    # --- Displaying Progress and Results (after rerun or on initial load if state exists) ---
    if st.session_state.progress_messages:
        # Display collected progress messages
        progress_placeholder.text_area("Log:", "".join([f"- {msg}\n" for msg in st.session_state.progress_messages]), height=400, disabled=True)
    else:
        progress_placeholder.info("Research log will appear here once processing starts.")

    if st.session_state.results:
        results_display_area.markdown(st.session_state.results, unsafe_allow_html=True)
        
        # Copy to Clipboard Button
        # Simplistic JS hack if streamlit_extras.st_copy_to_clipboard isn't available or suitable
        # This is a common workaround. `streamlit-extras` might have a better component.
        # For now, let's assume a placeholder or a simple JS solution.
        # If `streamlit_extras.st_copy_to_clipboard` was usable:
        # from streamlit_extras.st_copy_to_clipboard import st_copy_to_clipboard
        # st_copy_to_clipboard(st.session_state.results, "Copy Full Report")
        
        # Basic JS copy button (less ideal as it requires user interaction with a text area)
        # A true "click button to copy text" is harder without a dedicated component or more complex JS.
        # For this version, we'll just display results. Copy button can be a further refinement if a good component isn't found.
        st.markdown("---") # Separator before copy option
        # st.text_area("Copyable Report:", st.session_state.results, height=200, key="copy_report_area")
        # st.markdown("<small>You can select the text above and copy it manually.</small>", unsafe_allow_html=True)
        # If streamlit_extras has a copy button component like `stx.copy_button`, it would be:
        # import streamlit_ext as stx
        # if streamlit_extras_available and hasattr(stx, "copy_button"):
        #    stx.copy_button(st.session_state.results, "Copy Full Report")
        # else:
        #    st.write("To copy, select text from the report above.")
        # For now, just a note:
        results_display_area.markdown("*(To copy the report, please select the text and use Ctrl+C or Cmd+C.)*", unsafe_allow_html=True)

    else:
        results_display_area.info("Research findings will appear here.")

    st.sidebar.markdown("---")
    # Proactive warnings for essential configurations
    import os
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    ncbi_email = os.getenv("NCBI_EMAIL")

    if not azure_endpoint:
        st.sidebar.warning("⚠️ AZURE_OPENAI_ENDPOINT is not set. LLM features will be unavailable.")
    
    if not ncbi_email or ncbi_email == "your_email@example.com":
        st.sidebar.warning("⚠️ NCBI_EMAIL is not set or uses a placeholder. PubMed searches may be less reliable. Please set it in your environment.")

    st.sidebar.caption("Ensure Azure OpenAI and NCBI_EMAIL environment variables are correctly set as per the README.")


if __name__ == "__main__":
    main()
