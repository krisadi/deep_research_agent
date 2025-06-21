import streamlit as st
from dotenv import load_dotenv # For loading .env file
from utils import research_agent # research_agent will import its dependencies
from utils.research_agent import SOURCE_PDF, SOURCE_PUBMED, SOURCE_DUCKDUCKGO # Import constants
from utils.docx_exporter import create_research_report_docx, save_docx_to_bytes, generate_docx_filename
from typing import Set
import os # For environment variable checks

# Load environment variables from .env file at the very beginning
load_dotenv()

# --- Default Credentials (INSECURE - FOR DEMO/LOCAL USE ONLY) ---
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password" # Replace with something slightly less obvious if you must

# Custom CSS for professional styling
def load_css():
    """Load custom CSS for professional styling"""
    st.markdown("""
    <style>
    /* Professional Theme CSS */
    
    /* Global styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Professional header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        margin: 0;
        font-weight: 400;
    }
    
    /* Professional login form styling */
    .login-container {
        background: white;
        border-radius: 15px;
        padding: 2.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border: 1px solid #e1e8ed;
        max-width: 500px;
        margin: 2rem auto;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h2 {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .login-header p {
        color: #6c757d;
        font-size: 1rem;
        margin: 0;
    }
    
    .login-form {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 2rem;
        border: 1px solid #e9ecef;
    }
    
    /* Professional input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e1e8ed;
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Professional button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        padding: 12px 24px;
        transition: all 0.3s ease;
        border: none;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stButton > button[data-baseweb="button"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stButton > button[data-baseweb="button"]:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
    }
    
    .stButton > button:not([data-baseweb="button"]) {
        background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%) !important;
        color: white !important;
    }
    
    .stButton > button:not([data-baseweb="button"]):hover {
        background: linear-gradient(135deg, #8a9a9b 0%, #6f7c7d 100%) !important;
    }
    
    /* Professional card styling */
    .professional-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        transition: all 0.3s ease;
    }
    
    .professional-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .card-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Professional sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        border-right: 1px solid #dee2e6;
    }
    
    .css-1lcbmhc {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Professional status indicators */
    .status-success {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    .status-info {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    /* Custom loading animation */
    .brain-loading {
        display: inline-block;
        animation: brain-pulse 2s infinite;
    }
    
    @keyframes brain-pulse {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.7;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Custom spinner styling */
    .custom-spinner {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
        font-weight: 600;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .spinner-gear {
        font-size: 2em;
        margin-right: 15px;
        animation: gear-spin 2s linear infinite;
    }
    
    @keyframes gear-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Professional form elements */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e1e8ed;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stCheckbox > div > div {
        border-radius: 6px;
        border: 2px solid #e1e8ed;
    }
    
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e1e8ed;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stFileUploader > div {
        border-radius: 10px;
        border: 2px dashed #667eea;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    
    /* Professional alert styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        padding: 1rem 1.5rem;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
    }
    
    /* Error message styling */
    .stError {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    /* Warning message styling */
    .stWarning {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Professional results styling */
    .results-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid #e1e8ed;
        margin: 2rem 0;
    }
    
    .results-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 15px 15px 0 0;
        margin: -2rem -2rem 2rem -2rem;
        font-size: 1.4rem;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Professional progress log */
    .progress-log {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #667eea;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .progress-item {
        padding: 0.75rem 0;
        border-bottom: 1px solid #e9ecef;
        font-size: 0.95rem;
        color: #2c3e50;
    }
    
    .progress-item:last-child {
        border-bottom: none;
    }
    
    /* Professional source badges */
    .source-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .source-pdf { 
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
        color: white; 
    }
    
    .source-pubmed { 
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
        color: white; 
    }
    
    .source-web { 
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
        color: #2c3e50; 
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 { 
            font-size: 2rem; 
        }
        
        .login-container {
            margin: 1rem;
            padding: 1.5rem;
        }
        
        .professional-card {
            padding: 1rem;
        }
        
        .css-1d391kg { 
            width: 100% !important; 
        }
        
        .css-1lcbmhc { 
            width: 100% !important; 
        }
    }
    
    /* Professional typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
        color: #2c3e50;
    }
    
    p, div, span {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Professional color scheme */
    :root {
        --primary-color: #667eea;
        --primary-dark: #5a6fd8;
        --secondary-color: #764ba2;
        --secondary-dark: #6a4190;
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --error-color: #e74c3c;
        --info-color: #3498db;
        --light-bg: #f8f9fa;
        --border-color: #e1e8ed;
        --text-dark: #2c3e50;
        --text-light: #6c757d;
    }
    
    /* Professional multiselect styling */
    .stMultiSelect > div > div {
        border-radius: 8px;
        border: 2px solid #e1e8ed;
        transition: all 0.3s ease;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* PDF type filter styling */
    .pdf-type-filter {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 1px solid #90caf9;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .pdf-type-filter h4 {
        color: #1976d2;
        margin-bottom: 0.75rem;
        font-weight: 600;
    }
    
    /* Professional tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 1.5rem;
        width: 100%;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        flex: 1;
        min-width: 0;
        text-align: center;
        padding: 12px 16px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="false"] {
        background: white;
        color: #6c757d;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="false"]:hover {
        background: #e9ecef;
        color: #2c3e50;
        transform: translateY(-1px);
    }
    
    /* Make tabs container use full width */
    .stTabs {
        width: 100%;
    }
    
    /* Ensure tab list uses full width */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        width: 100%;
    }
    
    /* Tab content spacing */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    
    /* Better spacing between sections */
    .stTabs [data-baseweb="tab-panel"] > div {
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def show_login_form():
    """Display the login form with modern professional styling"""
    
    # Professional header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <h1 style="color: white; font-size: 2.8rem; margin-bottom: 0.5rem; font-weight: 700;">🧠 AI Research Agent</h1>
        <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.2rem; margin: 0;">Advanced Research Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 15px;
            padding: 2.5rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border: 1px solid #e1e8ed;
            margin: 2rem auto;
        ">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: #2c3e50; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">🔐 Login</h2>
                <p style="color: #6c757d; font-size: 1rem; margin: 0;">Enter your credentials to access the research platform</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            submit_button = st.form_submit_button("🚀 SIGN IN", use_container_width=True)
            
            if submit_button:
                if username == "admin" and password == "password":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful! Welcome to the Research Agent.")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
        
        # Demo credentials info
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border: 1px solid #90caf9;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            text-align: center;
        ">
            <h4 style="color: #1976d2; margin: 0 0 0.75rem 0; font-size: 1rem; font-weight: 600;">💡 Demo Credentials</h4>
            <p style="color: #424242; margin: 0.25rem 0; font-size: 0.9rem; font-family: 'Courier New', monospace;"><strong>Username:</strong> admin</p>
            <p style="color: #424242; margin: 0.25rem 0; font-size: 0.9rem; font-family: 'Courier New', monospace;"><strong>Password:</strong> password</p>
        </div>
        
        <div style="text-align: center; padding: 1.5rem; background: #f8f9fa; border-top: 1px solid #e9ecef; border-radius: 0 0 15px 15px; margin-top: 1.5rem; color: #6c757d; font-size: 0.9rem;">
            <p>© 2024 AI Research Agent. Secure access to advanced research capabilities.</p>
        </div>
        """, unsafe_allow_html=True)

def display_main_app():
    """Display the main application interface with professional styling"""
    
    # Professional header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 AI Research Agent</h1>
        <p>Advanced Research Platform powered by Azure OpenAI</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results' not in st.session_state:
        st.session_state.results = ""
    if 'progress_messages' not in st.session_state:
        st.session_state.progress_messages = []
    if 'source_data' not in st.session_state:
        st.session_state.source_data = {}  # Store individual source data
    if 'filtered_sources' not in st.session_state:
        st.session_state.filtered_sources = set()  # Track which sources to include
    if 'selected_source_index' not in st.session_state:
        st.session_state.selected_source_index = None  # Track which source is selected for sidebar
    if 'selected_source_type' not in st.session_state:
        st.session_state.selected_source_type = None  # Track source type for sidebar
    if 'selected_source_data_index' not in st.session_state:
        st.session_state.selected_source_data_index = None  # Track data index for sidebar

    # --- Sidebar Configuration ---
    with st.sidebar:
        # Welcome message
        if st.session_state.username:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; 
                        padding: 1.5rem; 
                        border-radius: 10px; 
                        margin-bottom: 1.5rem;
                        text-align: center;
                        border-left: 4px solid #3498db;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                <h2 style="margin: 0; font-size: 1.5rem;">👋 Welcome, {st.session_state.username.title()}!</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Ready to conduct advanced research</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Create tabs for better organization
        tab1, tab2 = st.tabs(["🔍 Research", "📄 Documents"])
        
        with tab1:
            st.markdown("""
            <div style="background: #2c3e50; 
                        color: white; 
                        padding: 1.5rem; 
                        border-radius: 10px; 
                        margin-bottom: 1.5rem;
                        text-align: center;
                        border-left: 4px solid #3498db;">
                <h2 style="margin: 0; font-size: 1.5rem;">⚙️ Research Configuration</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Configure your research parameters</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Query input in a styled container
            st.markdown("""
            <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; border: 1px solid #e9ecef;">
                <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">🔍 Research Query</h4>
            """, unsafe_allow_html=True)
            
            query = st.text_area("Enter your research question:", 
                                height=120,
                                placeholder="e.g., What are the latest developments in machine learning?",
                                help="Your main research question that will be used across all selected data sources.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Data sources in a styled container
            st.markdown("""
            <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; border: 1px solid #e9ecef;">
                <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">📊 Data Sources</h4>
            """, unsafe_allow_html=True)
        
            available_sources = [SOURCE_PUBMED, SOURCE_DUCKDUCKGO, SOURCE_PDF]
            default_sources = [SOURCE_PUBMED, SOURCE_DUCKDUCKGO] 

            selected_sources: Set[str] = set(st.multiselect(
                "Select information sources:",
                options=available_sources,
                default=default_sources,
                help="Choose which sources to query for information."
            ))

            # PDF document selection (simplified - just show what's available)
            if SOURCE_PDF in selected_sources:
                st.markdown("#### 📄 PDF Documents")
                
                # Get vector store from session state
                pdf_vector_store = st.session_state.get('pdf_vector_store', None)
                
                if pdf_vector_store and pdf_vector_store.vector_store:
                    # Get store status to show number of indexed documents
                    store_status = pdf_vector_store.get_store_status()
                    num_docs = store_status.get('num_docs', 0)
                    
                    # Additional check: try to access the docstore directly
                    try:
                        if hasattr(pdf_vector_store.vector_store, 'docstore') and pdf_vector_store.vector_store.docstore:
                            direct_doc_count = len(pdf_vector_store.vector_store.docstore._dict)
                            # Use the direct count if it's more reliable
                            if direct_doc_count > 0:
                                num_docs = direct_doc_count
                    except Exception as e:
                        pass
                    
                    if num_docs > 0:
                        st.success(f"✅ {num_docs} PDF chunk(s) indexed and ready for research")
                        
                        # Get unique PDF types from the vector store metadata
                        available_pdf_types = set()
                        if hasattr(pdf_vector_store, 'vector_store') and pdf_vector_store.vector_store:
                            # Try to get document metadata from the vector store
                            try:
                                # Access the document store to get metadata
                                if hasattr(pdf_vector_store.vector_store, 'docstore') and pdf_vector_store.vector_store.docstore:
                                    for doc_id in pdf_vector_store.vector_store.docstore._dict:
                                        doc = pdf_vector_store.vector_store.docstore._dict[doc_id]
                                        if hasattr(doc, 'metadata') and doc.metadata:
                                            pdf_type = doc.metadata.get('pdf_type', 'Unknown')
                                            available_pdf_types.add(pdf_type)
                            except Exception as e:
                                # Fallback to session state if vector store access fails
                                available_pdf_types = set(st.session_state.uploaded_pdfs.values())
                        
                        # If we couldn't get types from vector store, use session state
                        if not available_pdf_types and st.session_state.uploaded_pdfs:
                            available_pdf_types = set(st.session_state.uploaded_pdfs.values())
                        
                        if available_pdf_types:
                            available_pdf_types = sorted(list(available_pdf_types))
                            
                            # PDF type selection for research
                            st.markdown("**Select PDF types to include in research:**")
                            
                            selected_pdf_types_for_research = st.multiselect(
                                "Choose PDF types to analyze:",
                                options=available_pdf_types,
                                default=available_pdf_types,  # Include all by default
                                help="Select which types of PDFs to include in your research analysis"
                            )
                            
                            # Store selected types for research
                            st.session_state.selected_pdf_types_for_research = selected_pdf_types_for_research
                            
                            # Show summary of indexed PDFs by selected types
                            st.markdown("**Indexed PDFs by type:**")
                            for pdf_type in selected_pdf_types_for_research:
                                # Count documents of this type from vector store
                                type_count = 0
                                try:
                                    if hasattr(pdf_vector_store.vector_store, 'docstore') and pdf_vector_store.vector_store.docstore:
                                        for doc_id in pdf_vector_store.vector_store.docstore._dict:
                                            doc = pdf_vector_store.vector_store.docstore._dict[doc_id]
                                            if hasattr(doc, 'metadata') and doc.metadata:
                                                if doc.metadata.get('pdf_type') == pdf_type:
                                                    type_count += 1
                                except:
                                    # Fallback to session state count
                                    type_count = len([name for name, type_val in st.session_state.uploaded_pdfs.items() if type_val == pdf_type])
                                
                                st.markdown(f"• **{pdf_type}**: {type_count} chunk(s)")
                        else:
                            st.info("📋 Indexed documents available for research")
                    else:
                        st.warning("⚠️ No PDF chunks indexed. Switch to Documents tab to upload and index files.")
                else:
                    st.warning("⚠️ No PDFs indexed. Switch to Documents tab to upload files.")

            # PubMed options with increased limit
            if SOURCE_PUBMED in selected_sources:
                st.markdown("#### 🔬 PubMed Settings")
                max_pubmed_articles = st.slider("Max articles:", 
                                                min_value=1, max_value=100, value=10,
                                                help="Number of relevant PubMed articles to fetch (up to 100).")
            else:
                max_pubmed_articles = 0

            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add spacing before start button
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Start button in a prominent container
            st.markdown("""
            <div style="background: #2c3e50; 
                        border-radius: 8px; 
                        padding: 1rem; 
                        margin-bottom: 1.5rem; 
                        border: 1px solid #34495e;
                        text-align: center;">
                <h4 style="margin: 0 0 1rem 0; color: white;">🚀 Execute Research</h4>
            """, unsafe_allow_html=True)
            
            start_button = st.button("🚀 Start Research", 
                                    disabled=st.session_state.processing, 
                                    type="primary",
                                    use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown("""
            <div style="background: #2c3e50; 
                        color: white; 
                        padding: 1.5rem; 
                        border-radius: 10px; 
                        margin-bottom: 1.5rem;
                        text-align: center;
                        border-left: 4px solid #3498db;">
                <h2 style="margin: 0; font-size: 1.5rem;">📄 Document Management</h2>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Upload and categorize your documents</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize session state for uploaded PDFs if not exists
            if 'uploaded_pdfs' not in st.session_state:
                st.session_state.uploaded_pdfs = {}
            if 'uploaded_files' not in st.session_state:
                st.session_state.uploaded_files = {}
            
            # PDF type selection first
            st.markdown("#### 🏷️ Select PDF Type")
            st.markdown("Choose the type for the PDFs you want to upload:")
            
            # Predefined PDF types
            predefined_types = [
                "Patient_Data", "Social_Media_Data", "Research_Paper", 
                "Clinical_Trial", "Medical_Report", "Survey_Data",
                "Financial_Report", "Legal_Document", "Technical_Manual",
                "Academic_Paper", "News_Article", "Government_Report",
                "Business_Plan", "Marketing_Material", "Other"
            ]
            
            # Type selection
            selected_pdf_type = st.selectbox(
                "Choose PDF type:",
                options=predefined_types,
                index=len(predefined_types) - 1,  # Default to "Other"
                help="Select the type of content for the PDFs you want to upload"
            )
            
            # Custom type input
            st.markdown("#### ✏️ Custom PDF Type")
            custom_type = st.text_input(
                "Or enter a custom type:",
                placeholder="e.g., Clinical_Study_2024, Patient_Survey_Q1",
                help="Enter a custom type if none of the predefined types match"
            )
            
            # Use custom type if provided, otherwise use selected type
            current_pdf_type = custom_type.strip() if custom_type.strip() else selected_pdf_type
            
            # PDF upload section
            st.markdown("#### 📄 Upload PDF Documents")
            st.markdown(f"**Uploading PDFs as type: {current_pdf_type}**")
            
            uploaded_files = st.file_uploader(
                f"Upload PDF files (Type: {current_pdf_type}):", 
                accept_multiple_files=True, 
                type="pdf",
                help=f"Upload multiple PDF documents. All files will be categorized as '{current_pdf_type}'"
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} PDF(s) ready to upload as '{current_pdf_type}'")
                
                # Add spacing before submit button
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Submit button to confirm upload
                if st.button("📤 Submit Documents", type="primary", use_container_width=True):
                    # Store uploaded files in session state
                    for uploaded_file in uploaded_files:
                        st.session_state.uploaded_files[uploaded_file.name] = uploaded_file
                        st.session_state.uploaded_pdfs[uploaded_file.name] = current_pdf_type
                    
                    # Index the documents immediately
                    try:
                        with st.spinner("🔍 Indexing documents for search..."):
                            # Import required modules for indexing
                            from utils.document_indexer import DocumentIndexer
                            from utils.vector_store_handler import VectorStoreHandler
                            
                            # Get existing vector store or create new one
                            existing_vector_store = st.session_state.get('pdf_vector_store', None)
                            if existing_vector_store and existing_vector_store.vector_store:
                                vector_store = existing_vector_store
                            else:
                                vector_store = VectorStoreHandler()
                            
                            # Initialize indexer
                            doc_indexer = DocumentIndexer()
                            
                            all_pdf_chunks = []
                            
                            # Process each uploaded file
                            for uploaded_file in uploaded_files:
                                pdf_name = uploaded_file.name
                                pdf_type = current_pdf_type
                                
                                # Reset file stream for reading
                                uploaded_file.seek(0)
                                
                                # Process PDF and get chunks
                                chunks = doc_indexer.process_pdf(uploaded_file, pdf_name, pdf_type)
                                if chunks:
                                    all_pdf_chunks.extend(chunks)
                            
                            # Build or add to vector store if chunks were created
                            if all_pdf_chunks:
                                if existing_vector_store and existing_vector_store.vector_store:
                                    # Add to existing vector store
                                    vector_store.add_documents_to_store(all_pdf_chunks)
                                else:
                                    # Create new vector store
                                    vector_store.init_store_from_documents(all_pdf_chunks)
                                
                                # Check if vector store was created/updated
                                if vector_store.vector_store:
                                    # Store the vector store in session state
                                    st.session_state.pdf_vector_store = vector_store
                                    st.success(f"✅ Successfully uploaded and indexed {len(uploaded_files)} PDF(s) as '{current_pdf_type}'")
                                else:
                                    st.error("❌ Vector store creation/update failed")
                                    st.success(f"✅ Successfully uploaded {len(uploaded_files)} PDF(s) as '{current_pdf_type}' (indexing failed)")
                            else:
                                st.warning("⚠️ No text could be extracted from the uploaded PDFs")
                                st.success(f"✅ Successfully uploaded {len(uploaded_files)} PDF(s) as '{current_pdf_type}' (no text content found)")
                    
                    except Exception as e:
                        st.error(f"❌ Error during indexing: {str(e)}")
                        st.success(f"✅ Successfully uploaded {len(uploaded_files)} PDF(s) as '{current_pdf_type}' (indexing failed)")
                    
                    st.rerun()
                
                # Add spacing before document summary
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show current PDFs summary
                st.markdown("#### 📋 Current Documents")
                
                # Get vector store from session state
                pdf_vector_store = st.session_state.get('pdf_vector_store', None)
                
                if pdf_vector_store and pdf_vector_store.vector_store:
                    # Get store status to show number of indexed documents
                    store_status = pdf_vector_store.get_store_status()
                    num_docs = store_status.get('num_docs', 0)
                    
                    if num_docs > 0:
                        st.success(f"✅ {num_docs} PDF chunk(s) indexed and ready for research")
                        
                        # Get unique PDF types and counts from the vector store metadata
                        pdf_type_counts = {}
                        unique_files = set()
                        
                        try:
                            # Access the document store to get metadata
                            if hasattr(pdf_vector_store.vector_store, 'docstore') and pdf_vector_store.vector_store.docstore:
                                for doc_id in pdf_vector_store.vector_store.docstore._dict:
                                    doc = pdf_vector_store.vector_store.docstore._dict[doc_id]
                                    if hasattr(doc, 'metadata') and doc.metadata:
                                        pdf_type = doc.metadata.get('pdf_type', 'Unknown')
                                        source_file = doc.metadata.get('source', 'Unknown')
                                        
                                        pdf_type_counts[pdf_type] = pdf_type_counts.get(pdf_type, 0) + 1
                                        unique_files.add(source_file)
                        except Exception as e:
                            # Fallback to session state if vector store access fails
                            st.warning(f"⚠️ Could not read vector store metadata: {str(e)}")
                            if st.session_state.uploaded_pdfs:
                                for pdf_name, pdf_type in st.session_state.uploaded_pdfs.items():
                                    pdf_type_counts[pdf_type] = pdf_type_counts.get(pdf_type, 0) + 1
                                    unique_files.add(pdf_name)
                        
                        # Display indexed documents by type
                        if pdf_type_counts:
                            st.markdown("**Indexed documents by type:**")
                            for pdf_type, count in sorted(pdf_type_counts.items()):
                                st.markdown(f"• **{pdf_type}**: {count} chunk(s)")
                            
                            st.markdown(f"**Total:** {len(unique_files)} file(s) → {num_docs} chunk(s)")
                        else:
                            st.info("📋 Indexed documents available for research")
                    else:
                        st.warning("⚠️ No PDF chunks indexed. Upload and submit files to make them available for research.")
                elif st.session_state.uploaded_pdfs:
                    # Fallback to session state if no vector store
                    st.info("📋 Documents uploaded but not yet indexed")
                    
                    # Group by type
                    type_counts = {}
                    for pdf_name, pdf_type in st.session_state.uploaded_pdfs.items():
                        type_counts[pdf_type] = type_counts.get(pdf_type, 0) + 1
                    
                    st.markdown("**Uploaded documents by type:**")
                    for pdf_type, count in sorted(type_counts.items()):
                        st.markdown(f"• **{pdf_type}**: {count} file(s)")
                else:
                    st.info("No PDFs currently uploaded")
                
                # Show pending uploads if any
                if uploaded_files:
                    if st.session_state.uploaded_pdfs:
                        st.markdown("**Ready to submit:**")
                    else:
                        st.markdown("**Ready to submit:**")
                    st.markdown(f"• **{current_pdf_type}**: {len(uploaded_files)} file(s) pending submission")
                
                # Add spacing before clear button
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Clear all button
                if st.button("🗑️ Clear All Documents", type="secondary", use_container_width=True):
                    st.session_state.uploaded_pdfs = {}
                    st.session_state.uploaded_files = {}
                    st.rerun()
            else:
                st.info("📁 No PDFs uploaded yet. Select a type and upload files to get started.")
        
        # Bottom section with status and actions (outside tabs)
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #e9ecef;">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">📊 System Status</h4>
        """, unsafe_allow_html=True)
        
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        ncbi_email = os.getenv("NCBI_EMAIL")

        if not azure_endpoint or not azure_deployment:
            st.markdown('<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 0.5rem; margin-bottom: 0.5rem; font-size: 0.8rem; color: #856404;">🧠 LLM: Not Configured</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 0.5rem; margin-bottom: 0.5rem; font-size: 0.8rem; color: #155724;">🧠 LLM: Ready</div>', unsafe_allow_html=True)
        
        if not ncbi_email or ncbi_email == "your_email@example.com":
            st.markdown('<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 0.5rem; margin-bottom: 0.5rem; font-size: 0.8rem; color: #856404;">🔬 PubMed: Limited</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 0.5rem; margin-bottom: 0.5rem; font-size: 0.8rem; color: #155724;">🔬 PubMed: Ready</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action buttons at bottom of sidebar
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #e9ecef;">
            <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">🔧 Actions</h4>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Logout", key="logout_button", help="Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.results = ""
                st.session_state.progress_messages = []
                st.session_state.source_data = {}
                st.session_state.filtered_sources = set()
                st.session_state.selected_source_index = None
                st.session_state.selected_source_type = None
                st.session_state.selected_source_data_index = None
                st.session_state.uploaded_pdfs = {}
                st.session_state.uploaded_files = {}
                st.session_state.selected_pdf_types_for_research = []
                # Keep the vector store - don't clear indexed documents
                # st.session_state.pdf_vector_store = None
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset", key="reset_button", help="Reset Session", use_container_width=True):
                st.session_state.processing = False
                st.session_state.results = ""
                st.session_state.progress_messages = []
                st.session_state.source_data = {}
                st.session_state.filtered_sources = set()
                st.session_state.selected_source_index = None
                st.session_state.selected_source_type = None
                st.session_state.selected_source_data_index = None
                st.session_state.uploaded_pdfs = {}
                st.session_state.uploaded_files = {}
                st.session_state.selected_pdf_types_for_research = []
                # Keep the vector store - don't clear indexed documents
                # st.session_state.pdf_vector_store = None
                st.success("Session reset successfully! (Indexed documents preserved)")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Main Content Area ---
    
    # Research execution
    if start_button:
        if not query.strip():
            st.error("⚠️ Please enter a research question.")
        elif not selected_sources:
            st.error("⚠️ Please select at least one data source.")
        elif SOURCE_PDF in selected_sources:
            # Check if PDFs are available for research (either indexed or uploaded)
            pdf_vector_store = st.session_state.get('pdf_vector_store', None)
            
            # Check for indexed PDFs using multiple methods
            has_indexed_pdfs = False
            if pdf_vector_store and pdf_vector_store.vector_store:
                # Try direct docstore access first
                try:
                    if hasattr(pdf_vector_store.vector_store, 'docstore') and pdf_vector_store.vector_store.docstore:
                        direct_doc_count = len(pdf_vector_store.vector_store.docstore._dict)
                        has_indexed_pdfs = direct_doc_count > 0
                except Exception as e:
                    # Fallback to store status
                    store_status = pdf_vector_store.get_store_status()
                    has_indexed_pdfs = store_status.get('num_docs', 0) > 0
            
            has_uploaded_pdfs = st.session_state.uploaded_pdfs
            
            if not has_indexed_pdfs and not has_uploaded_pdfs:
                st.error(f"⚠️ '{SOURCE_PDF}' is selected, but no PDF files are available for research. Please upload and submit PDFs in the Documents tab.")
            elif not has_indexed_pdfs and has_uploaded_pdfs:
                st.error(f"⚠️ '{SOURCE_PDF}' is selected, but uploaded PDFs need to be submitted and indexed. Please click 'Submit Documents' in the Documents tab.")
            else:
                # PDFs are available, proceed with research
                st.session_state.processing = True
                st.session_state.results = "" 
                st.session_state.progress_messages = [] 
                st.session_state.current_query = query  # Store query for export
                
                def streamlit_progress_update(message: str):
                    st.session_state.progress_messages.append(message)

                # Execute research with custom loading spinner
                show_loading_spinner("🧠 AI is thinking... Performing research")
                try:
                    # Get uploaded files from session state if PDF source is selected
                    uploaded_files = None
                    if SOURCE_PDF in selected_sources and st.session_state.uploaded_pdfs:
                        # Filter PDFs based on selected types for research
                        selected_types = st.session_state.get('selected_pdf_types_for_research', [])
                        if selected_types:
                            # Get PDFs that match the selected types
                            filtered_pdfs = []
                            for pdf_name, pdf_type in st.session_state.uploaded_pdfs.items():
                                if pdf_type in selected_types:
                                    if pdf_name in st.session_state.uploaded_files:
                                        filtered_pdfs.append(st.session_state.uploaded_files[pdf_name])
                            uploaded_files = filtered_pdfs
                        else:
                            # If no types selected, use all PDFs
                            uploaded_files = list(st.session_state.uploaded_files.values())
                    
                    # Use pre-indexed vector store if available
                    pdf_vector_store = st.session_state.get('pdf_vector_store', None)
                    
                    # If we have a vector store, we don't need to pass uploaded files
                    # The research agent will use the vector store directly
                    if pdf_vector_store and pdf_vector_store.vector_store:
                        uploaded_files = None  # Vector store will be used instead
                    
                    research_result = research_agent.conduct_research(
                            query=query,
                            selected_data_sources=selected_sources,
                            uploaded_pdf_files=uploaded_files if SOURCE_PDF in selected_sources else None,
                            pdf_types=st.session_state.get('selected_pdf_types_for_research', []) if SOURCE_PDF in selected_sources else None,
                            max_pubmed_articles=max_pubmed_articles if SOURCE_PUBMED in selected_sources else 0,
                            on_progress_update=streamlit_progress_update,
                            pdf_vector_store=pdf_vector_store  # Pass pre-indexed vector store
                        )
                    
                    # Handle new return format
                    if isinstance(research_result, dict):
                        st.session_state.results = research_result['report']
                        st.session_state.source_data = research_result['source_data']
                        st.session_state.is_raw_data = research_result['is_raw_data']
                        # Initialize filtered sources to include all sources
                        st.session_state.filtered_sources = set(range(len(st.session_state.source_data.get('pdf_sources', []) + 
                                                                       st.session_state.source_data.get('pubmed_sources', []) + 
                                                                       st.session_state.source_data.get('web_sources', []))))
                    else:
                        # Handle legacy string return format
                        st.session_state.results = research_result
                        st.session_state.source_data = {}
                        st.session_state.is_raw_data = True
                        st.session_state.filtered_sources = set()
                        
                except Exception as e:
                    st.session_state.results = f"An unexpected critical error occurred: {str(e)}"
                    st.session_state.progress_messages.append(f"CRITICAL ERROR: {str(e)}")
                    st.error(f"Critical error during research: {str(e)}") 
                finally:
                    st.session_state.processing = False
                    st.rerun()
        else:
            # No PDF source selected, proceed with research
            st.session_state.processing = True
            st.session_state.results = "" 
            st.session_state.progress_messages = [] 
            st.session_state.current_query = query  # Store query for export
            
            def streamlit_progress_update(message: str):
                st.session_state.progress_messages.append(message)

            # Execute research with custom loading spinner
            show_loading_spinner("🧠 AI is thinking... Performing research")
            try:
                # Get uploaded files from session state if PDF source is selected
                uploaded_files = None
                if SOURCE_PDF in selected_sources and st.session_state.uploaded_pdfs:
                    # Filter PDFs based on selected types for research
                    selected_types = st.session_state.get('selected_pdf_types_for_research', [])
                    if selected_types:
                        # Get PDFs that match the selected types
                        filtered_pdfs = []
                        for pdf_name, pdf_type in st.session_state.uploaded_pdfs.items():
                            if pdf_type in selected_types:
                                if pdf_name in st.session_state.uploaded_files:
                                    filtered_pdfs.append(st.session_state.uploaded_files[pdf_name])
                        uploaded_files = filtered_pdfs
                    else:
                        # If no types selected, use all PDFs
                        uploaded_files = list(st.session_state.uploaded_files.values())
                
                # Use pre-indexed vector store if available
                pdf_vector_store = st.session_state.get('pdf_vector_store', None)
                
                # If we have a vector store, we don't need to pass uploaded files
                # The research agent will use the vector store directly
                if pdf_vector_store and pdf_vector_store.vector_store:
                    uploaded_files = None  # Vector store will be used instead
                
                research_result = research_agent.conduct_research(
                        query=query,
                        selected_data_sources=selected_sources,
                        uploaded_pdf_files=uploaded_files if SOURCE_PDF in selected_sources else None,
                        pdf_types=st.session_state.get('selected_pdf_types_for_research', []) if SOURCE_PDF in selected_sources else None,
                        max_pubmed_articles=max_pubmed_articles if SOURCE_PUBMED in selected_sources else 0,
                        on_progress_update=streamlit_progress_update,
                        pdf_vector_store=pdf_vector_store  # Pass pre-indexed vector store
                    )
                
                # Handle new return format
                if isinstance(research_result, dict):
                    st.session_state.results = research_result['report']
                    st.session_state.source_data = research_result['source_data']
                    st.session_state.is_raw_data = research_result['is_raw_data']
                    # Initialize filtered sources to include all sources
                    st.session_state.filtered_sources = set(range(len(st.session_state.source_data.get('pdf_sources', []) + 
                                                                   st.session_state.source_data.get('pubmed_sources', []) + 
                                                                   st.session_state.source_data.get('web_sources', []))))
                else:
                    # Handle legacy string return format
                    st.session_state.results = research_result
                    st.session_state.source_data = {}
                    st.session_state.is_raw_data = True
                    st.session_state.filtered_sources = set()
                    
            except Exception as e:
                st.session_state.results = f"An unexpected critical error occurred: {str(e)}"
                st.session_state.progress_messages.append(f"CRITICAL ERROR: {str(e)}")
                st.error(f"Critical error during research: {str(e)}") 
            finally:
                st.session_state.processing = False
                st.rerun()

    # --- Results Display ---
    if st.session_state.results:
        st.markdown("---")
        
        # Display results with professional styling
        st.markdown("""
        <div class="results-container">
            <div class="results-header">
                📊 Research Results
            </div>
        """, unsafe_allow_html=True)
        
        # Display mode indicator
        if hasattr(st.session_state, 'is_raw_data') and st.session_state.is_raw_data:
            st.markdown('<div class="status-info">📋 Raw Data Mode (LLM Unavailable)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-success">🤖 AI-Powered Synthesis Mode</div>', unsafe_allow_html=True)
        
        # Display main content
        st.markdown("### 📝 Research Findings")
        st.markdown(st.session_state.results, unsafe_allow_html=True)
        
        # Add PDF type summary if PDF sources exist
        pdf_sources = st.session_state.source_data.get('pdf_sources', [])
        if pdf_sources:
            st.markdown("### 🏷️ PDF Type Summary")
            pdf_type_counts = {}
            for source in pdf_sources:
                pdf_type = source.get('pdf_type', 'Unknown')
                pdf_type_counts[pdf_type] = pdf_type_counts.get(pdf_type, 0) + 1
            
            # Display PDF type breakdown
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**PDF Types Processed:**")
                for pdf_type, count in sorted(pdf_type_counts.items()):
                    st.markdown(f"• **{pdf_type}**: {count} chunk(s)")
            
            with col2:
                st.markdown("**Total PDF Chunks:**")
                st.markdown(f"**{len(pdf_sources)}** chunks from **{len(set([s.get('source', '') for s in pdf_sources]))}** file(s)")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Source filtering and regeneration section
        if st.session_state.source_data and any(st.session_state.source_data.values()):
            st.markdown("---")
            st.markdown("## 🔧 Source Management")
            
            # Create main content and sidebar layout
            main_col, sidebar_col = st.columns([2, 1])
            
            with main_col:
                st.markdown("### 📋 Available Sources")
                
                # Add PDF type filter if PDF sources exist
                pdf_sources = st.session_state.source_data.get('pdf_sources', [])
                if pdf_sources:
                    # Get unique PDF types
                    pdf_types = list(set([source.get('pdf_type', 'Unknown') for source in pdf_sources]))
                    pdf_types.sort()
                    
                    st.markdown("""
                    <div class="pdf-type-filter">
                        <h4>🏷️ Filter by PDF Type</h4>
                    """, unsafe_allow_html=True)
                    
                    selected_pdf_types = st.multiselect(
                        "Select PDF types to include:",
                        options=pdf_types,
                        default=pdf_types,  # Include all by default
                        help="Filter sources by PDF type. Only selected types will be shown."
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Display sources with checkboxes for filtering
                all_sources = []
                source_types = []
                source_indices = []  # Track original indices for each source type
                
                # Collect all sources with proper indexing
                pdf_start = 0
                pubmed_start = len(st.session_state.source_data.get('pdf_sources', []))
                web_start = pubmed_start + len(st.session_state.source_data.get('pubmed_sources', []))
                
                # PDF sources (with type filtering)
                for i, source in enumerate(st.session_state.source_data.get('pdf_sources', [])):
                    pdf_type = source.get('pdf_type', 'Unknown')
                    # Only include if type is selected or if no PDF sources exist (show all)
                    if not pdf_sources or pdf_type in selected_pdf_types:
                        all_sources.append(f"📄 {source.get('title', 'PDF Document')}")
                        source_types.append('pdf')
                        source_indices.append(i)
                
                # PubMed sources
                for i, source in enumerate(st.session_state.source_data.get('pubmed_sources', [])):
                    all_sources.append(f"🔬 {source.get('title', 'PubMed Article')}")
                    source_types.append('pubmed')
                    source_indices.append(i)
                
                # Web sources
                for i, source in enumerate(st.session_state.source_data.get('web_sources', [])):
                    all_sources.append(f"🌐 {source.get('title', 'Web Search Result')}")
                    source_types.append('web')
                    source_indices.append(i)
                
                # Create checkboxes for each source
                selected_sources_for_regeneration = []
                
                # Add "Select All" checkbox
                select_all = st.checkbox("✅ Select All Sources", value=len(st.session_state.filtered_sources) == len(all_sources), key="select_all")
                
                # Handle select all logic
                if select_all:
                    # If select all is checked, select all sources
                    selected_sources_for_regeneration = list(range(len(all_sources)))
                else:
                    # If select all is unchecked, clear all selections
                    selected_sources_for_regeneration = []
                    
                    # Show individual checkboxes for selective choosing
                    for i, (source, source_type) in enumerate(zip(all_sources, source_types)):
                        col_check, col_link = st.columns([0.8, 0.2])
                        
                        with col_check:
                            checkbox_value = st.checkbox(
                                source, 
                                value=False,  # Always start unchecked when select all is off
                                key=f"source_{i}"
                            )
                            if checkbox_value:
                                selected_sources_for_regeneration.append(i)
                        
                        with col_link:
                            if st.button("🔍", key=f"view_{i}", help="Preview excerpt"):
                                st.session_state.selected_source_index = i
                                st.session_state.selected_source_type = source_type
                                st.session_state.selected_source_data_index = source_indices[i]
                
                # Update filtered sources
                st.session_state.filtered_sources = set(selected_sources_for_regeneration)
                
                # Selection info
                total_sources = len(all_sources)
                selected_count = len(st.session_state.filtered_sources)
                st.info(f"**Selected:** {selected_count}/{total_sources} sources")
                
                # Regenerate button
                if st.button("🔄 Regenerate Insights from Selected Sources", type="primary", use_container_width=True):
                    if selected_count > 0:
                        st.session_state.processing = True
                        st.session_state.progress_messages = []
                        
                        def regeneration_progress_update(message: str):
                            st.session_state.progress_messages.append(message)
                        
                        # Add initial progress message
                        regeneration_progress_update("🔄 Starting regeneration process...")
                        
                        # Filter the source data based on selection
                        regeneration_progress_update("📊 Filtering selected sources...")
                        filtered_data = {
                            'pdf_sources': [],
                            'pubmed_sources': [],
                            'web_sources': []
                        }
                        
                        pdf_idx = 0
                        pubmed_idx = 0
                        web_idx = 0
                        
                        for i in range(total_sources):
                            if i in st.session_state.filtered_sources:
                                if source_types[i] == 'pdf':
                                    if pdf_idx < len(st.session_state.source_data.get('pdf_sources', [])):
                                        filtered_data['pdf_sources'].append(st.session_state.source_data['pdf_sources'][pdf_idx])
                                    pdf_idx += 1
                                elif source_types[i] == 'pubmed':
                                    if pubmed_idx < len(st.session_state.source_data.get('pubmed_sources', [])):
                                        filtered_data['pubmed_sources'].append(st.session_state.source_data['pubmed_sources'][pubmed_idx])
                                    pubmed_idx += 1
                                elif source_types[i] == 'web':
                                    if web_idx < len(st.session_state.source_data.get('web_sources', [])):
                                        filtered_data['web_sources'].append(st.session_state.source_data['web_sources'][web_idx])
                                    web_idx += 1
                        
                        regeneration_progress_update(f"✅ Filtered {len(filtered_data['pdf_sources'])} PDF, {len(filtered_data['pubmed_sources'])} PubMed, and {len(filtered_data['web_sources'])} web sources")
                        
                        # Execute regeneration with custom loading spinner
                        try:
                            # Import required modules for regeneration
                            from utils.llm_handler import get_llm_response
                            
                            # Create a simplified research function for regeneration
                            def regenerate_insights(filtered_data, query, progress_callback):
                                # Combine all filtered sources
                                progress_callback("📝 Combining source content...")
                                all_texts = []
                                sources_summary = []
                                
                                for source in filtered_data['pdf_sources']:
                                    all_texts.append(source.get('content', ''))
                                    sources_summary.append(source.get('title', 'PDF Document'))
                                
                                for source in filtered_data['pubmed_sources']:
                                    all_texts.append(source.get('content', ''))
                                    sources_summary.append(source.get('title', 'PubMed Article'))
                                
                                for source in filtered_data['web_sources']:
                                    all_texts.append(source.get('content', ''))
                                    sources_summary.append(source.get('title', 'Web Search Result'))
                                
                                progress_callback(f"📚 Combined content from {len(sources_summary)} sources")
                                
                                if not all_texts:
                                    progress_callback("⚠️ No sources selected for regeneration")
                                    return {
                                        'report': "No sources selected for regeneration.",
                                        'is_raw_data': True
                                    }
                                
                                # Check LLM availability
                                progress_callback("🔍 Checking LLM availability...")
                                llm_test_response = get_llm_response("Test", "You are a helpful assistant.")
                                llm_available = not (llm_test_response.startswith("Error:") or "Azure OpenAI" in llm_test_response or "Language Model" in llm_test_response)
                                
                                if not llm_available:
                                    progress_callback("⚠️ LLM not available, generating raw data report")
                                    # Return simplified format without raw data section
                                    final_report = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px;">Filtered Research Report: "{query}"</h1>

<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>ℹ️ Note:</strong> LLM processing is not available. Use the Source Management section below to view individual source excerpts and regenerate insights from selected sources.
</div>

<h2 style="color: #34495e; margin-top: 30px;">📚 Selected Sources ({len(sources_summary)})</h2>
<div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
"""
                                    for src in sources_summary:
                                        final_report += f"<div style='margin: 8px 0;'>• {src}</div>"
                                    final_report += "</div>"
                                    
                                    final_report += f"""
<hr style="margin: 30px 0; border: none; border-top: 2px solid #e1e8ed;">
<div style="background: #e8f5e8; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; margin: 20px 0;">
    <strong>📊 Summary:</strong> {len(sources_summary)} sources were processed. Use the Source Management section below to view individual excerpts and regenerate insights from selected sources.
</div>
</div>
"""
                                    return {
                                        'report': final_report,
                                        'is_raw_data': True
                                    }
                                
                                # LLM is available - synthesize
                                progress_callback("🧠 LLM available, synthesizing insights...")
                                combined_text = "\n\n".join(all_texts)
                                
                                if len(combined_text) > 50000:  # Limit context
                                    progress_callback("📏 Truncating content to fit context limits...")
                                    combined_text = combined_text[:50000]
                                
                                progress_callback("🤖 Generating AI-synthesized response...")
                                llm_prompt = f"""
You are a highly proficient AI research assistant. Your task is to synthesize information from the provided documents to answer the user's research query.

User's Research Query: "{query}"

Provided Documents (filtered selection):
{combined_text}

Instructions:
1. Carefully read all provided document excerpts.
2. Based *only* on the information within these documents, provide a comprehensive answer to the user's research query.
3. Structure your answer clearly. Use bullet points or numbered lists for key findings if appropriate.
4. If the documents contain conflicting information, acknowledge it if relevant to the query.
5. If the documents do not contain sufficient information to answer the query thoroughly, explicitly state that and indicate what information might be missing.
6. When possible, reference the source of key pieces of information.
7. Your response should be objective and analytical.

Begin your synthesized answer below:
"""
                                
                                llm_response = get_llm_response(llm_prompt)
                                
                                if "Error:" in llm_response and ("Azure OpenAI" in llm_response or "Language Model" in llm_response):
                                    progress_callback("❌ Failed to get LLM response")
                                    return {
                                        'report': f"Failed to get a response from the Language Model. Details: {llm_response}",
                                        'is_raw_data': True
                                    }
                                
                                progress_callback("✅ Successfully generated AI-synthesized response")
                                final_report = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px;">Filtered AI Research Report: "{query}"</h1>

<div style="background: #e8f5e8; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>🤖 AI Synthesis:</strong> This report has been synthesized from {len(sources_summary)} selected sources.
</div>

<h2 style="color: #34495e; margin-top: 30px;">📚 Selected Sources</h2>
<div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
"""
                                for src in sources_summary:
                                    final_report += f"<div style='margin: 8px 0;'>• {src}</div>"
                                final_report += "</div>"
                                
                                final_report += """
<hr style="margin: 30px 0; border: none; border-top: 2px solid #e1e8ed;">
<h2 style="color: #2c3e50; margin-top: 30px;">💡 AI-Synthesized Answer</h2>
<div style="background: white; border: 1px solid #e1e8ed; border-radius: 8px; padding: 25px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); line-height: 1.6; font-size: 1.1em;">
"""
                                final_report += llm_response
                                final_report += """
</div>
</div>
"""
                                
                                return {
                                    'report': final_report,
                                    'is_raw_data': False
                                }
                            
                            show_loading_spinner("🧠 AI is thinking... Generating insights from selected sources")
                            regeneration_result = regenerate_insights(filtered_data, query, regeneration_progress_update)
                            st.session_state.results = regeneration_result['report']
                            st.session_state.is_raw_data = regeneration_result['is_raw_data']
                            regeneration_progress_update("🎉 Regeneration completed successfully!")
                            
                        except Exception as e:
                            regeneration_progress_update(f"❌ Error during regeneration: {str(e)}")
                            st.error(f"Error during regeneration: {str(e)}")
                        finally:
                            st.session_state.processing = False
                            st.rerun()
            
            with sidebar_col:
                # Professional pop-up style excerpt panel
                if hasattr(st.session_state, 'selected_source_index') and st.session_state.selected_source_index is not None:
                    source_type = st.session_state.selected_source_type
                    data_index = st.session_state.selected_source_data_index
                    
                    # Professional pop-up styling with better colors
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <h3 style="color: white; margin: 0; font-size: 1.2em; font-weight: 600;">📖 Source Excerpt</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if source_type == 'pdf':
                        source_data = st.session_state.source_data['pdf_sources'][data_index]
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                            border-radius: 8px;
                            padding: 15px;
                            margin-bottom: 15px;
                            color: white;
                            font-weight: 600;
                        ">
                            📄 PDF Document
                        </div>
                        """, unsafe_allow_html=True)
                    elif source_type == 'pubmed':
                        source_data = st.session_state.source_data['pubmed_sources'][data_index]
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                            border-radius: 8px;
                            padding: 15px;
                            margin-bottom: 15px;
                            color: white;
                            font-weight: 600;
                        ">
                            🔬 PubMed Article
                        </div>
                        """, unsafe_allow_html=True)
                    else:  # web
                        source_data = st.session_state.source_data['web_sources'][data_index]
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                            border-radius: 8px;
                            padding: 15px;
                            margin-bottom: 15px;
                            color: #2c3e50;
                            font-weight: 600;
                        ">
                            🌐 Web Search Result
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display source title with professional styling
                    st.markdown(f"""
                    <div style="
                        background: #ffffff;
                        border-left: 4px solid #667eea;
                        padding: 12px;
                        margin-bottom: 15px;
                        border-radius: 4px;
                        border: 1px solid #e1e8ed;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    ">
                        <strong style="color: #1f2937; font-size: 1.1em;">{source_data.get('title', 'Source')}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display content with professional styling
                    content = source_data.get('content', '')
                    
                    st.text_area(
                        "📋 Copyable Content",
                        value=content,
                        height=300,
                        key="sidebar_content",
                        help="You can copy the content from this text area"
                    )
                    
                    # Display metadata with professional styling
                    if source_type == 'pubmed':
                        pmid = source_data.get('pmid', '')
                        url = source_data.get('url', '')
                        if pmid:
                            st.markdown(f"""
                            <div style="
                                background: #e3f2fd;
                                border: 1px solid #bbdefb;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                            ">
                                <strong style="color: #1976d2;">PMID:</strong> {pmid}
                            </div>
                            """, unsafe_allow_html=True)
                        if url:
                            st.markdown(f"""
                            <div style="
                                background: #e8f5e8;
                                border: 1px solid #c8e6c9;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                                word-wrap: break-word;
                                overflow-wrap: break-word;
                                max-width: 100%;
                            ">
                                <strong style="color: #388e3c;">URL:</strong> <a href="{url}" target="_blank" style="color: #1976d2; text-decoration: none; word-break: break-all; display: inline-block; max-width: 100%;">{url}</a>
                            </div>
                            """, unsafe_allow_html=True)
                    elif source_type == 'web':
                        url = source_data.get('url', '')
                        if url:
                            st.markdown(f"""
                            <div style="
                                background: #e8f5e8;
                                border: 1px solid #c8e6c9;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                                word-wrap: break-word;
                                overflow-wrap: break-word;
                                max-width: 100%;
                            ">
                                <strong style="color: #388e3c;">URL:</strong> <a href="{url}" target="_blank" style="color: #1976d2; text-decoration: none; word-break: break-all; display: inline-block; max-width: 100%;">{url}</a>
                            </div>
                            """, unsafe_allow_html=True)
                    elif source_type == 'pdf':
                        source_file = source_data.get('source', '')
                        chunk_num = source_data.get('chunk_number', '')
                        page_num = source_data.get('page_number', '')
                        pdf_type = source_data.get('pdf_type', '')
                        if source_file:
                            st.markdown(f"""
                            <div style="
                                background: #fff3e0;
                                border: 1px solid #ffcc02;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                            ">
                                <strong style="color: #f57c00;">File:</strong> {source_file}
                            </div>
                            """, unsafe_allow_html=True)
                        if pdf_type:
                            st.markdown(f"""
                            <div style="
                                background: #e1f5fe;
                                border: 1px solid #81d4fa;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                            ">
                                <strong style="color: #0277bd;">Type:</strong> {pdf_type}
                            </div>
                            """, unsafe_allow_html=True)
                        if page_num:
                            st.markdown(f"""
                            <div style="
                                background: #e8f5e8;
                                border: 1px solid #c8e6c9;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                            ">
                                <strong style="color: #388e3c;">Page:</strong> {page_num}
                            </div>
                            """, unsafe_allow_html=True)
                        if chunk_num:
                            st.markdown(f"""
                            <div style="
                                background: #f3e5f5;
                                border: 1px solid #ce93d8;
                                border-radius: 6px;
                                padding: 10px;
                                margin-bottom: 10px;
                            ">
                                <strong style="color: #7b1fa2;">Chunk:</strong> {chunk_num}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Close button with professional styling
                    if st.button("❌ Close Excerpt", key="close_excerpt", use_container_width=True):
                        st.session_state.selected_source_index = None
                        st.session_state.selected_source_type = None
                        st.session_state.selected_source_data_index = None
                        st.rerun()
                else:
                    # Empty state with professional styling
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <h3 style="color: white; margin: 0; font-size: 1.2em; font-weight: 600;">📖 Source Excerpt</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="
                        background: #f8f9fa;
                        border: 2px dashed #dee2e6;
                        border-radius: 8px;
                        padding: 30px;
                        text-align: center;
                        color: #6c757d;
                    ">
                        <div style="font-size: 2em; margin-bottom: 10px;">👆</div>
                        <strong>Click the 🔍 button next to any source to view its excerpt here.</strong>
                    </div>
                    """, unsafe_allow_html=True)

    # --- Progress Log ---
    if st.session_state.progress_messages:
        # Progress bar (always visible)
        if st.session_state.processing:
            progress_bar = st.progress(0)
            # Calculate progress based on number of messages
            progress_value = min(len(st.session_state.progress_messages) / 10, 1.0)  # Assume 10 steps for full progress
            progress_bar.progress(progress_value)
        
        # Collapsible progress log
        with st.expander("📝 Research Process Log", expanded=False):
            st.markdown("""
            <div class="progress-log">
            """, unsafe_allow_html=True)
            
            for i, msg in enumerate(st.session_state.progress_messages):
                st.markdown(f"""
                <div class="progress-item">
                    <strong>{i+1}.</strong> {msg}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Initial State ---
    elif not st.session_state.results and not st.session_state.processing:
        st.markdown("""
        <div class="professional-card">
            <div class="card-header">🎯 Ready to Research</div>
            <p style="color: #6c757d; font-size: 1.1rem; line-height: 1.6;">
                Configure your research query and data sources in the sidebar, then click "Start Research" to begin your analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_loading_spinner(message="Processing..."):
    """Display a custom loading spinner with gear icon"""
    st.markdown(f"""
    <div class="custom-spinner">
        <div class="spinner-gear">⚙️</div>
        <div>{message}</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        layout="wide", 
        page_title="AI Research Agent",
        page_icon="🧠",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Add custom CSS to make sidebar wider
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        width: 400px !important;
        min-width: 400px !important;
    }
    
    /* Make main content full screen when sidebar is collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: 0 !important;
    }
    
    /* Ensure main content takes full width when sidebar is collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main {
        width: 100% !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
    }
    
    /* Additional rules for sidebar collapse */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container > div {
        max-width: 100% !important;
    }
    
    /* Force full width when sidebar is collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container,
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container > div,
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container > div > div {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Alternative selector for sidebar collapse */
    .css-1d391kg[aria-expanded="false"] ~ .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: 0 !important;
    }
    
    .css-1d391kg[aria-expanded="false"] ~ .main {
        width: 100% !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.authenticated:
        display_main_app()
    else:
        show_login_form()

if __name__ == "__main__":
    main()
