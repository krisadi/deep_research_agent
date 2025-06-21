# Core research logic for the agent
from . import pubmed_fetcher
from . import llm_handler
from . import duckduckgo_searcher
from .document_indexer import DocumentIndexer
from .vector_store_handler import VectorStoreHandler

from typing import List, Dict, Optional, Callable, Any, Set, Union
import io

# Configuration
MAX_CONTEXT_CHARS_FOR_LLM = 32000 # Increased slightly, adjust based on model (e.g., gpt-3.5-turbo-16k)
MAX_DUCKDUCKGO_RESULTS = 3
MAX_PDF_CHUNKS_TO_LLM = 5 # Max relevant PDF chunks to feed to LLM from vector search

# Data source constants
SOURCE_PDF = "Indexed PDFs"
SOURCE_PUBMED = "PubMed Articles"
SOURCE_DUCKDUCKGO = "DuckDuckGo Search"


def conduct_research(
    query: str,
    selected_data_sources: Set[str],
    uploaded_pdf_files: Optional[List[Union[io.BytesIO, Any]]] = None, # Streamlit UploadedFile is IO-like
    pdf_types: Optional[Dict[str, str]] = None,  # NEW: PDF type mapping
    max_pubmed_articles: int = 3,
    on_progress_update: Optional[Callable[[str], None]] = None,
    pdf_vector_store: Optional[Any] = None,  # Pre-indexed vector store
    # Allow passing existing vector store and indexer for session persistence if implemented later
    # For now, they are created per call if PDF source is selected.
    # vector_store_handler: Optional[VectorStoreHandler] = None, 
    # document_indexer: Optional[DocumentIndexer] = None
) -> Dict[str, Any]:
    """
    Conducts research based on a query, selected data sources, optional PDFs, and PubMed articles.
    Returns a dictionary with results and structured source data.
    """
    
    def _progress(message: str):
        if on_progress_update:
            on_progress_update(message)
        print(message)

    full_text_corpus: List[str] = []
    sources_summary: List[str] = []
    processing_errors: List[str] = []
    
    # Structured data for individual sources
    source_data = {
        'pdf_sources': [],
        'pubmed_sources': [],
        'web_sources': []
    }

    _progress("Starting research process...")
    _progress(f"Query: {query}")
    _progress(f"Selected data sources: {', '.join(selected_data_sources)}")

    # Initialize handlers if PDF processing is needed
    # For simplicity in this iteration, VectorStoreHandler and DocumentIndexer are created on each call
    # if PDFs are a selected source. A more advanced version would persist the index across calls/sessions.
    if SOURCE_PDF in selected_data_sources and uploaded_pdf_files:
        if pdf_vector_store and pdf_vector_store.vector_store:
            _progress("Using pre-indexed PDF vector store...")
        else:
            try:
                _progress("Initializing Document Indexer and Vector Store for PDF processing...")
                doc_indexer = DocumentIndexer() # Uses default chunk_size/overlap
                pdf_vector_store = VectorStoreHandler() # Uses default embedding model
                
                all_pdf_chunks = []
                for uploaded_file in uploaded_pdf_files:
                    pdf_name = getattr(uploaded_file, 'name', 'uploaded_pdf_file')
                    pdf_type = pdf_types.get(pdf_name, 'Unknown') if pdf_types else 'Unknown'
                    _progress(f"Processing PDF: {pdf_name} (Type: {pdf_type}) for indexing...")
                    
                    # Ensure the file stream is in a compatible format (BytesIO)
                    # Streamlit's UploadedFile is already IO-like.
                    # We might need to read its content if the underlying library expects bytes.
                    # For PyPDF2 and pdf2image, passing the stream directly or after .read() works.
                    
                    # Reset stream for multiple reads if necessary (pdf_processor used to do this)
                    uploaded_file.seek(0) 
                    
                    try:
                        chunks = doc_indexer.process_pdf(uploaded_file, pdf_name, pdf_type)
                        if chunks:
                            all_pdf_chunks.extend(chunks)
                            _progress(f"Successfully processed and chunked '{pdf_name}' (Type: {pdf_type}). Found {len(chunks)} chunks.")
                        else:
                            warning_msg = f"Warning: No text chunks extracted from PDF '{pdf_name}' (Type: {pdf_type}). It might be empty or purely image-based with OCR issues."
                            _progress(warning_msg)
                            processing_errors.append(warning_msg)
                    except Exception as e_pdf_proc:
                        err_msg = f"Error processing PDF '{pdf_name}' (Type: {pdf_type}): {e_pdf_proc}"
                        _progress(err_msg)
                        processing_errors.append(err_msg)

                if all_pdf_chunks:
                    _progress(f"Indexing {len(all_pdf_chunks)} total chunks from all PDFs...")
                    pdf_vector_store.init_store_from_documents(all_pdf_chunks)
                    _progress("PDF chunks indexed successfully in FAISS.")
                    _progress(f"Vector store status: {pdf_vector_store.get_store_status()}")
                else:
                    _progress("No PDF chunks were available to build the vector index.")
                    pdf_vector_store = None # Ensure it's None if no docs were indexed

            except Exception as e_init: # Catch errors from DocumentIndexer or VectorStoreHandler init
                err_msg = f"Failed to initialize PDF processing pipeline: {e_init}"
                _progress(err_msg)
                processing_errors.append(err_msg)
                pdf_vector_store = None # Disable PDF search for this run

    # 1. Retrieve relevant chunks from Indexed PDFs
    if SOURCE_PDF in selected_data_sources and pdf_vector_store and pdf_vector_store.vector_store:
        _progress(f"Searching indexed PDF chunks for query: '{query}'...")
        try:
            relevant_pdf_chunks = pdf_vector_store.search_relevant_chunks(query, k=MAX_PDF_CHUNKS_TO_LLM)
            if relevant_pdf_chunks:
                _progress(f"Found {len(relevant_pdf_chunks)} relevant chunks from indexed PDFs.")
                
                # Filter chunks by PDF type if types are specified
                filtered_chunks = relevant_pdf_chunks
                if pdf_types and not uploaded_pdf_files:
                    # We're using pre-indexed vector store, filter by type from metadata
                    selected_types = set(pdf_types.values()) if isinstance(pdf_types, dict) else set()
                    if selected_types:
                        filtered_chunks = []
                        for chunk_doc in relevant_pdf_chunks:
                            chunk_type = chunk_doc.metadata.get('pdf_type', 'Unknown')
                            if chunk_type in selected_types:
                                filtered_chunks.append(chunk_doc)
                        _progress(f"Filtered to {len(filtered_chunks)} chunks from selected types: {', '.join(selected_types)}")
                
                for chunk_doc in filtered_chunks:
                    pdf_type = chunk_doc.metadata.get('pdf_type', 'Unknown')
                    chunk_text = f"--- START OF RELEVANT PDF CHUNK (Source: {chunk_doc.metadata.get('source', 'N/A')}, Type: {pdf_type}, Chunk: {chunk_doc.metadata.get('chunk_number', 'N/A')}) ---\n"
                    chunk_text += chunk_doc.page_content
                    chunk_text += f"\n--- END OF RELEVANT PDF CHUNK (Source: {chunk_doc.metadata.get('source', 'N/A')}) ---"
                    full_text_corpus.append(chunk_text)
                    sources_summary.append(f"Retrieved Chunk from PDF: {chunk_doc.metadata.get('source', 'N/A')} (Type: {pdf_type}, Chunk {chunk_doc.metadata.get('chunk_number', 'N/A')})")
                    
                    # Store source data for filtering
                    source_data['pdf_sources'].append({
                        'title': f"PDF: {chunk_doc.metadata.get('source', 'N/A')} (Type: {pdf_type}, Chunk {chunk_doc.metadata.get('chunk_number', 'N/A')})",
                        'content': chunk_doc.page_content,
                        'source': chunk_doc.metadata.get('source', 'N/A'),
                        'chunk_number': chunk_doc.metadata.get('chunk_number', 'N/A'),
                        'pdf_type': pdf_type,
                        'page_number': chunk_doc.metadata.get('page_number', 'N/A')
                    })
            else:
                _progress("No relevant chunks found in indexed PDFs for the query.")
        except Exception as e_pdf_search:
            err_msg = f"Error searching PDF vector store: {e_pdf_search}"
            _progress(err_msg)
            processing_errors.append(err_msg)
    elif SOURCE_PDF in selected_data_sources and not uploaded_pdf_files and not pdf_vector_store:
        _progress("PDF source selected, but no PDF files were uploaded or indexed.")
    elif SOURCE_PDF in selected_data_sources and (not pdf_vector_store or not pdf_vector_store.vector_store) and uploaded_pdf_files:
         _progress("PDFs were uploaded and PDF source selected, but PDF vector index is not available (likely due to earlier processing errors).")


    # 2. Fetch articles from PubMed
    if SOURCE_PUBMED in selected_data_sources:
        import os # For getenv
        ncbi_email = os.getenv("NCBI_EMAIL")
        if not ncbi_email or ncbi_email == "your_email@example.com":
            warn_msg = "NCBI_EMAIL environment variable is not set or uses a placeholder. PubMed search functionality might be limited or unreliable. Please configure it for optimal results."
            _progress(f"Warning: {warn_msg}")
            processing_errors.append(warn_msg)
            # Continue with the search, pubmed_fetcher has its own console warning.

        _progress(f"Fetching up to {max_pubmed_articles} PubMed articles for query: '{query}'...")
        if not query:
            _progress("Skipping PubMed search as query is empty (though source was selected).")
        else:
            pubmed_articles = pubmed_fetcher.fetch_articles_for_query(query, max_articles=max_pubmed_articles)
            if pubmed_articles:
                _progress(f"Found {len(pubmed_articles)} PubMed articles.")
                for article in pubmed_articles:
                    pmid = article.get('pmid', 'N/A')
                    title = article.get('title', 'N/A')
                    abstract = article.get('abstract', 'N/A')
                    if abstract and abstract != 'N/A':
                        article_text = f"--- START OF PUBMED ARTICLE (PMID: {pmid}) ---\n"
                        article_text += f"Title: {title}\nAbstract: {abstract}\n"
                        article_text += f"--- END OF PUBMED ARTICLE (PMID: {pmid}) ---"
                        full_text_corpus.append(article_text)
                        sources_summary.append(f"PubMed Article (PMID: {pmid}): {title}")
                        
                        # Store source data for filtering
                        source_data['pubmed_sources'].append({
                            'title': f"PubMed: {title}",
                            'content': f"Title: {title}\nAbstract: {abstract}",
                            'pmid': pmid,
                            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })
                        
                        _progress(f"Added PubMed article to corpus: PMID {pmid} - {title[:50]}...")
                    else:
                        _progress(f"Skipping PubMed article PMID {pmid} due to missing abstract: {title[:50]}...")
            else:
                _progress("No relevant articles found on PubMed for the query.")
    
    # 3. Fetch search results from DuckDuckGo
    if SOURCE_DUCKDUCKGO in selected_data_sources:
        _progress(f"Fetching up to {MAX_DUCKDUCKGO_RESULTS} DuckDuckGo search results for query: '{query}'...")
        if not query:
            _progress("Skipping DuckDuckGo search as query is empty (though source was selected).")
        else:
            ddg_results = duckduckgo_searcher.search_duckduckgo(query, num_results=MAX_DUCKDUCKGO_RESULTS)
            if ddg_results:
                _progress(f"Found {len(ddg_results)} DuckDuckGo search results.")
                for result in ddg_results:
                    title = result.get('title', 'N/A')
                    snippet = result.get('snippet', 'N/A')
                    url = result.get('url', '#')
                    if snippet and snippet != 'N/A':
                        search_text = f"--- START OF DUCKDUCKGO SEARCH RESULT SNIPPET ---\n"
                        search_text += f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n"
                        search_text += f"--- END OF DUCKDUCKGO SEARCH RESULT SNIPPET ---"
                        full_text_corpus.append(search_text)
                        sources_summary.append(f"DuckDuckGo Snippet: {title} ({url})")
                        
                        # Store source data for filtering
                        source_data['web_sources'].append({
                            'title': f"Web: {title}",
                            'content': f"Title: {title}\nURL: {url}\nSnippet: {snippet}",
                            'url': url
                        })
                        
                        _progress(f"Added DuckDuckGo snippet to corpus: {title[:50]}...")
                    else:
                         _progress(f"Skipping DuckDuckGo result due to missing snippet: {title[:50]}...")
            else:
                _progress("No relevant search results found on DuckDuckGo for the query.")

    # Check if any information was gathered
    if not full_text_corpus:
        _progress("No text content gathered from any selected and successful sources.")
        final_report_msg = "No information was gathered from the selected sources for your query. "
        final_report_msg += "Please try a different query, upload relevant documents if using PDF source, or check source selection."
        if processing_errors:
            final_report_msg += "\n\nProcessing Issues Encountered:\n" + "\n".join(processing_errors)
        return {
            'report': final_report_msg,
            'source_data': source_data,
            'is_raw_data': True
        }

    _progress(f"Aggregated text from {len(sources_summary)} distinct source entries.")
    
    # Check if LLM is available before processing
    _progress("Checking LLM availability...")
    llm_test_response = llm_handler.get_llm_response("Test", "You are a helpful assistant.")
    llm_available = not (llm_test_response.startswith("Error:") or "Azure OpenAI" in llm_test_response or "Language Model" in llm_test_response)
    
    if not llm_available:
        _progress("LLM is not available. Displaying raw data from each source separately.")
        
        # Create a simplified report with just the raw data
        final_report = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px;">Research Report: "{query}"</h1>

<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>ℹ️ Note:</strong> LLM processing is not available. Use the Source Management section below to view individual source excerpts and regenerate insights.
</div>
"""
        
        if processing_errors:
            final_report += """
<h2 style="color: #e74c3c; margin-top: 30px;">⚠️ Processing Issues</h2>
<div style="background: #fdf2f2; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0;">
"""
            for err in processing_errors:
                final_report += f"<div style='margin: 8px 0; color: #c0392b;'>• {err}</div>"
            final_report += "</div>"
        
        final_report += f"""
<hr style="margin: 30px 0; border: none; border-top: 2px solid #e1e8ed;">
<div style="background: #e8f5e8; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; margin: 20px 0;">
    <strong>📊 Summary:</strong> {len(sources_summary)} sources were processed. Use the Source Management section below to view individual excerpts and regenerate insights from selected sources.
</div>
</div>
"""
        
        _progress("Research process completed (raw data mode).")
        return {
            'report': final_report,
            'source_data': source_data,
            'is_raw_data': True
        }
    
    # LLM is available - proceed with normal processing
    _progress("LLM is available. Proceeding with synthesis...")
    combined_text = "\n\n".join(full_text_corpus)

    if len(combined_text) > MAX_CONTEXT_CHARS_FOR_LLM:
        _progress(f"Warning: Combined text length ({len(combined_text)} chars) exceeds limit ({MAX_CONTEXT_CHARS_FOR_LLM} chars). Truncating context.")
        combined_text = combined_text[:MAX_CONTEXT_CHARS_FOR_LLM]

    _progress("Formulating prompt for LLM...")
    llm_prompt = f"""
You are a highly proficient AI research assistant. Your task is to synthesize information from the provided documents to answer the user's research query.

User's Research Query: "{query}"

Provided Documents (these may include PubMed abstracts, web search snippets, and relevant chunks from PDF documents with type classifications):
{combined_text}

Instructions:
1. Carefully read all provided document excerpts.
2. Based *only* on the information within these documents, provide a comprehensive answer to the user's research query.
3. Structure your answer clearly. Use bullet points or numbered lists for key findings if appropriate.
4. If the documents contain conflicting information, acknowledge it if relevant to the query.
5. If the documents do not contain sufficient information to answer the query thoroughly, explicitly state that and indicate what information might be missing. Do not invent information or search outside these provided texts.
6. When possible, reference the source of key pieces of information by mentioning the document title, PDF source and type, PMID, or web search result title (e.g., "According to PDF 'report.pdf' (Type: Patient_Data) chunk...", "The abstract of PMID:123456 states...", "The DuckDuckGo snippet for 'XYZ' suggests...").
7. Pay attention to PDF type classifications (e.g., Patient_Data, Social_Media_Data, Research_Paper, etc.) as they may indicate the nature and reliability of the information source.
8. Your response should be objective and analytical.

Begin your synthesized answer below:
"""

    _progress("Sending request to LLM. This may take a moment...")
    llm_response = llm_handler.get_llm_response(llm_prompt)
    
    if "Error:" in llm_response and ("Azure OpenAI" in llm_response or "Language Model" in llm_response):
        _progress(f"LLM interaction failed: {llm_response}")
        return {
            'report': f"Failed to get a response from the Language Model. Details: {llm_response}",
            'source_data': source_data,
            'is_raw_data': True
        }

    _progress("LLM response received.")

    final_report = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px;">AI Research Report: "{query}"</h1>

<div style="background: #e8f5e8; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>🤖 AI Synthesis:</strong> This report has been synthesized by an AI model from multiple information sources.
</div>
"""
    
    if sources_summary:
        final_report += """
<h2 style="color: #34495e; margin-top: 30px;">📚 Sources Consulted</h2>
<div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
"""
        for src in sources_summary:
            final_report += f"<div style='margin: 8px 0;'>• {src}</div>"
        final_report += "</div>"
    else:
        final_report += """
<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>⚠️ Note:</strong> No primary information sources were successfully processed or found relevant.
</div>
"""
    
    if processing_errors:
        final_report += """
<h2 style="color: #e74c3c; margin-top: 30px;">⚠️ Processing Issues</h2>
<div style="background: #fdf2f2; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0;">
"""
        for err in processing_errors:
            final_report += f"<div style='margin: 8px 0; color: #c0392b;'>• {err}</div>"
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
    
    _progress("Research process completed.")
    return {
        'report': final_report,
        'source_data': source_data,
        'is_raw_data': False
    }
