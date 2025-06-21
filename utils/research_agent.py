# Core research logic for the agent
from . import pubmed_fetcher
from . import llm_handler
from . import duckduckgo_searcher
from .document_indexer import DocumentIndexer
from .vector_store_handler import VectorStoreHandler

from typing import List, Dict, Optional, Callable, Any, Set
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
    uploaded_pdf_files: Optional[List[io.BytesIO]] = None, # Streamlit UploadedFile is IO-like
    max_pubmed_articles: int = 3,
    on_progress_update: Optional[Callable[[str], None]] = None,
    # Allow passing existing vector store and indexer for session persistence if implemented later
    # For now, they are created per call if PDF source is selected.
    # vector_store_handler: Optional[VectorStoreHandler] = None, 
    # document_indexer: Optional[DocumentIndexer] = None
) -> str:
    """
    Conducts research based on a query, selected data sources, optional PDFs, and PubMed articles.
    """
    
    def _progress(message: str):
        if on_progress_update:
            on_progress_update(message)
        print(message)

    full_text_corpus: List[str] = []
    sources_summary: List[str] = []
    processing_errors: List[str] = []

    _progress("Starting research process...")
    _progress(f"Query: {query}")
    _progress(f"Selected data sources: {', '.join(selected_data_sources)}")

    # Initialize handlers if PDF processing is needed
    # For simplicity in this iteration, VectorStoreHandler and DocumentIndexer are created on each call
    # if PDFs are a selected source. A more advanced version would persist the index across calls/sessions.
    pdf_vector_store = None
    if SOURCE_PDF in selected_data_sources and uploaded_pdf_files:
        try:
            _progress("Initializing Document Indexer and Vector Store for PDF processing...")
            doc_indexer = DocumentIndexer() # Uses default chunk_size/overlap
            pdf_vector_store = VectorStoreHandler() # Uses default embedding model
            
            all_pdf_chunks = []
            for uploaded_file in uploaded_pdf_files:
                pdf_name = getattr(uploaded_file, 'name', 'uploaded_pdf_file')
                _progress(f"Processing PDF: {pdf_name} for indexing...")
                
                # Ensure the file stream is in a compatible format (BytesIO)
                # Streamlit's UploadedFile is already IO-like.
                # We might need to read its content if the underlying library expects bytes.
                # For PyPDF2 and pdf2image, passing the stream directly or after .read() works.
                
                # Reset stream for multiple reads if necessary (pdf_processor used to do this)
                uploaded_file.seek(0) 
                
                try:
                    chunks = doc_indexer.process_pdf(uploaded_file, pdf_name)
                    if chunks:
                        all_pdf_chunks.extend(chunks)
                        _progress(f"Successfully processed and chunked '{pdf_name}'. Found {len(chunks)} chunks.")
                    else:
                        warning_msg = f"Warning: No text chunks extracted from PDF '{pdf_name}'. It might be empty or purely image-based with OCR issues."
                        _progress(warning_msg)
                        processing_errors.append(warning_msg)
                except Exception as e_pdf_proc:
                    err_msg = f"Error processing PDF '{pdf_name}': {e_pdf_proc}"
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
                for chunk_doc in relevant_pdf_chunks:
                    chunk_text = f"--- START OF RELEVANT PDF CHUNK (Source: {chunk_doc.metadata.get('source', 'N/A')}, Chunk: {chunk_doc.metadata.get('chunk_number', 'N/A')}) ---\n"
                    chunk_text += chunk_doc.page_content
                    chunk_text += f"\n--- END OF RELEVANT PDF CHUNK (Source: {chunk_doc.metadata.get('source', 'N/A')}) ---"
                    full_text_corpus.append(chunk_text)
                    sources_summary.append(f"Retrieved Chunk from PDF: {chunk_doc.metadata.get('source', 'N/A')} (Chunk {chunk_doc.metadata.get('chunk_number', 'N/A')})")
            else:
                _progress("No relevant chunks found in indexed PDFs for the query.")
        except Exception as e_pdf_search:
            err_msg = f"Error searching PDF vector store: {e_pdf_search}"
            _progress(err_msg)
            processing_errors.append(err_msg)
    elif SOURCE_PDF in selected_data_sources and not uploaded_pdf_files:
        _progress("PDF source selected, but no PDF files were uploaded.")
    elif SOURCE_PDF in selected_data_sources and (not pdf_vector_store or not pdf_vector_store.vector_store) and uploaded_pdf_files:
         _progress("PDFs were uploaded and PDF source selected, but PDF vector index is not available (likely due to earlier processing errors).")


    # 2. Fetch articles from PubMed
    if SOURCE_PUBMED in selected_data_sources:
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
        return final_report_msg

    _progress(f"Aggregated text from {len(sources_summary)} distinct source entries.")
    combined_text = "\n\n".join(full_text_corpus)

    if len(combined_text) > MAX_CONTEXT_CHARS_FOR_LLM:
        _progress(f"Warning: Combined text length ({len(combined_text)} chars) exceeds limit ({MAX_CONTEXT_CHARS_FOR_LLM} chars). Truncating context.")
        combined_text = combined_text[:MAX_CONTEXT_CHARS_FOR_LLM]

    _progress("Formulating prompt for LLM...")
    llm_prompt = f"""
You are a highly proficient AI research assistant. Your task is to synthesize information from the provided documents to answer the user's research query.

User's Research Query: "{query}"

Provided Documents (these may include PubMed abstracts, web search snippets, and relevant chunks from PDF documents):
{combined_text}

Instructions:
1. Carefully read all provided document excerpts.
2. Based *only* on the information within these documents, provide a comprehensive answer to the user's research query.
3. Structure your answer clearly. Use bullet points or numbered lists for key findings if appropriate.
4. If the documents contain conflicting information, acknowledge it if relevant to the query.
5. If the documents do not contain sufficient information to answer the query thoroughly, explicitly state that and indicate what information might be missing. Do not invent information or search outside these provided texts.
6. When possible, reference the source of key pieces of information by mentioning the document title, PDF source, PMID, or web search result title (e.g., "According to PDF 'report.pdf' chunk...", "The abstract of PMID:123456 states...", "The DuckDuckGo snippet for 'XYZ' suggests...").
7. Your response should be objective and analytical.

Begin your synthesized answer below:
"""

    _progress("Sending request to LLM. This may take a moment...")
    llm_response = llm_handler.get_llm_response(llm_prompt)
    
    if "Error:" in llm_response and ("Azure OpenAI" in llm_response or "Language Model" in llm_response):
        _progress(f"LLM interaction failed: {llm_response}")
        return f"Failed to get a response from the Language Model. Details: {llm_response}"

    _progress("LLM response received.")

    final_report = f"## Research Report for Query: \"{query}\"\n\n"
    if sources_summary:
        final_report += "### Sources Consulted (or relevant portions thereof):\n"
        for src in sources_summary:
            final_report += f"- {src}\n"
    else:
        final_report += "No primary information sources were successfully processed or found relevant.\n"
    
    if processing_errors:
        final_report += "\n### Processing Issues Encountered:\n"
        for err in processing_errors:
            final_report += f"- {err}\n"
            
    final_report += "\n---\n### Synthesized Answer from LLM:\n"
    final_report += llm_response
    
    _progress("Research process completed.")
    return final_report
