import streamlit as st
from dotenv import load_dotenv # For loading .env file
from utils import research_agent # research_agent will import its dependencies
from utils.pubmed_fetcher import SOURCE_NAME as PUBMED_SOURCE_NAME
from utils.duckduckgo_searcher import SOURCE_NAME as DUCKDUCKGO_SOURCE_NAME
from utils.docx_exporter import create_research_report_docx, save_docx_to_bytes, generate_docx_filename
from typing import Set, List, Dict, Any
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
    
        # Get available sources dynamically from the research agent
        available_sources = research_agent.get_available_sources()
        # Default to all available sources
        default_sources = available_sources

        selected_sources: Set[str] = set(st.multiselect(
            "Select information sources:",
            options=available_sources,
            default=default_sources,
            help="Choose which sources to query for information."
        ))

        # PubMed options with increased limit
        if PUBMED_SOURCE_NAME in selected_sources:
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
                research_result = research_agent.conduct_research(
                        query=query,
                        selected_data_sources=selected_sources,
                        max_pubmed_articles=max_pubmed_articles if PUBMED_SOURCE_NAME in selected_sources else 0,
                        on_progress_update=streamlit_progress_update,
                    )
                
                # Handle new return format
                if isinstance(research_result, dict):
                    st.session_state.results = research_result['report']
                    st.session_state.source_data = research_result['source_data']
                    st.session_state.is_raw_data = research_result['is_raw_data']
                    # Initialize filtered sources to include all sources
                    total_sources = sum(len(v) for v in st.session_state.source_data.values())
                    st.session_state.filtered_sources = set(range(total_sources))
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
                
                # Display sources with checkboxes for filtering
                # Create a flattened list of all sources with their original keys and indices
                flat_sources_with_info = []
                for source_key, sources in st.session_state.source_data.items():
                    for i, source_item in enumerate(sources):
                        flat_sources_with_info.append({
                            "key": source_key,
                            "index": i,
                            "item": source_item
                        })

                # Create checkboxes for each source
                selected_indices = []
                
                # Add "Select All" checkbox
                select_all_default = len(st.session_state.filtered_sources) == len(flat_sources_with_info)
                select_all = st.checkbox("✅ Select All Sources", value=select_all_default, key="select_all")
                
                # Update filtered sources based on select all state
                if select_all:
                    st.session_state.filtered_sources = set(range(len(flat_sources_with_info)))
                elif len(st.session_state.filtered_sources) == len(flat_sources_with_info):
                    # If select all was unchecked, clear all selections
                    st.session_state.filtered_sources = set()

                # Show individual checkboxes
                for i, source_info in enumerate(flat_sources_with_info):
                    source_item = source_info["item"]
                    source_key = source_info["key"]
                    # Format the source key into a user-friendly name
                    source_type_name = source_key.replace('_sources', '').replace('_', ' ').strip().title()
                    
                    is_selected = i in st.session_state.filtered_sources
                    
                    col_check, col_link = st.columns([0.8, 0.2])
                    
                    with col_check:
                        checkbox_value = st.checkbox(
                            f"📄 [{source_type_name}] {source_item.get('title', 'Source')}", 
                            value=is_selected,
                            key=f"source_{i}"
                        )
                        if checkbox_value:
                            selected_indices.append(i)
                        else:
                            # Remove from filtered sources if unchecked
                            if i in st.session_state.filtered_sources:
                                st.session_state.filtered_sources.remove(i)
                    
                    with col_link:
                        if st.button("🔍", key=f"view_{i}", help="Preview excerpt"):
                            st.session_state.selected_source_key = source_info["key"]
                            st.session_state.selected_source_data_index = source_info["index"]
                            st.rerun()

                # Update filtered sources with current selections
                st.session_state.filtered_sources = set(selected_indices)
                
                # Selection info
                total_sources = len(flat_sources_with_info)
                selected_count = len(st.session_state.filtered_sources)
                st.info(f"**Selected:** {selected_count}/{total_sources} sources")
                
                # Regenerate button
                if st.button("🔄 Regenerate Insights from Selected Sources", type="primary", use_container_width=True):
                    if selected_count > 0:
                        st.session_state.processing = True
                        st.session_state.progress_messages = []
                        
                        def regeneration_progress_update(message: str):
                            st.session_state.progress_messages.append(message)
                        
                        regeneration_progress_update("🔄 Starting regeneration process...")
                        
                        # Filter the source data based on selection
                        regeneration_progress_update("📊 Filtering selected sources...")
                        filtered_data: Dict[str, List[Dict[str, Any]]] = {}
                        for i in st.session_state.filtered_sources:
                            source_info = flat_sources_with_info[i]
                            key = source_info["key"]
                            item = source_info["item"]
                            if key not in filtered_data:
                                filtered_data[key] = []
                            filtered_data[key].append(item)
                        
                        show_loading_spinner("🧠 AI is thinking... Generating insights from selected sources")
                        
                        try:
                            # Call the new, centralized regeneration function
                            regeneration_result = research_agent.regenerate_report_from_sources(
                                query=st.session_state.current_query,
                                source_data=filtered_data,
                                on_progress_update=regeneration_progress_update
                            )
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
                if 'selected_source_key' in st.session_state and st.session_state.selected_source_key is not None:
                    source_key = st.session_state.selected_source_key
                    data_index = st.session_state.selected_source_data_index
                    source_data_item = st.session_state.source_data[source_key][data_index]
                    
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
                    
                    st.markdown(f"#### {source_data_item.get('title', 'Source')}")
                    
                    content = source_data_item.get('content', '')
                    st.text_area("📋 Copyable Content", value=content, height=300, key="sidebar_content")
                    
                    url = source_data_item.get('url', '')
                    if url:
                        st.markdown(f"**URL:** [{url}]({url})")
                    
                    metadata = source_data_item.get('metadata', {})
                    if metadata:
                        st.json(metadata)

                    if st.button("❌ Close Excerpt", key="close_excerpt", use_container_width=True):
                        st.session_state.selected_source_key = None
                        st.session_state.selected_source_data_index = None
                        st.rerun()
                else:
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
                    st.info("Click the 🔍 button next to any source to view its excerpt here.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Progress Log ---
    if st.session_state.progress_messages:
        if st.session_state.processing:
            st.progress(len(st.session_state.progress_messages) / 10.0)
        
        with st.expander("📝 Research Process Log", expanded=False):
            st.markdown("""
            <div class="progress-log">
            """, unsafe_allow_html=True)
            for msg in st.session_state.progress_messages:
                st.markdown(f'<div class="progress-item">{msg}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Export Section ---
    if st.session_state.results:
        st.markdown("---")
        st.markdown("## 📄 Export Research Report")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Use a unique key that changes when results are updated
            export_key = f"export_docx_{hash(st.session_state.results) % 10000}"
            if st.button("📄 Export to DOCX", key=export_key, help="Export the report to a DOCX file", use_container_width=True, type="primary"):
                try:
                    # Create filtered source data for export based on current selections
                    filtered_source_data = {}
                    if st.session_state.filtered_sources:
                        for i in st.session_state.filtered_sources:
                            source_info = flat_sources_with_info[i]
                            key = source_info["key"]
                            item = source_info["item"]
                            if key not in filtered_source_data:
                                filtered_source_data[key] = []
                            filtered_source_data[key].append(item)
                    else:
                        # If no sources selected, use all source data
                        filtered_source_data = st.session_state.source_data
                    
                    # Generate the DOCX document with the latest results and filtered data
                    doc = create_research_report_docx(
                        query=st.session_state.get('current_query', 'Research Report'),
                        results=st.session_state.results,  # This will be the latest results after regeneration
                        is_raw_data=st.session_state.is_raw_data,
                        source_data=filtered_source_data  # Use filtered data instead of all data
                    )
                    # Save to a byte stream
                    doc_bytes = save_docx_to_bytes(doc)
                    # Generate a filename
                    file_name = generate_docx_filename(st.session_state.get('current_query', 'Research_Report'))
                    
                    # Provide for download
                    st.download_button(
                        label="📥 Download DOCX",
                        data=doc_bytes,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    st.success("✅ DOCX report is ready for download!")
                except Exception as e:
                    st.error(f"❌ Failed to generate DOCX: {e}")
    
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
