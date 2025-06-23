# Core research logic for the agent
from . import pubmed_fetcher
from . import llm_handler
from . import duckduckgo_searcher
from . import arxiv_fetcher
from . import wikipedia_fetcher
from . import pdf_fetcher_1
from . import pdf_fetcher_2
from . import pdf_fetcher_3
from .vector_store_handler import VectorStoreHandler

from typing import List, Dict, Optional, Callable, Any, Set, Union
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MAX_CONTEXT_CHARS_FOR_LLM = 32000
MAX_DUCKDUCKGO_RESULTS = 3
MAX_PDF_CHUNKS_TO_LLM = 5

# Data source constants - will be populated dynamically
AVAILABLE_SOURCES: Dict[str, Optional[Callable[..., Any]]] = {}
SOURCE_PDF = "Indexed PDFs" # This remains static as it's a special case

def _get_boolean_env_var(var_name: str) -> bool:
    """Helper to get boolean value from environment variable."""
    return os.getenv(var_name, 'false').lower() in ('true', '1', 't')

def _initialize_sources():
    """Dynamically initializes the available data sources based on .env configuration."""
    global AVAILABLE_SOURCES
    AVAILABLE_SOURCES = {SOURCE_PDF: None} # Start with PDF source

    if _get_boolean_env_var('ENABLE_WIKIPEDIA_SEARCH'):
        AVAILABLE_SOURCES[wikipedia_fetcher.SOURCE_NAME] = wikipedia_fetcher.fetch_wikipedia_data
    if _get_boolean_env_var('ENABLE_DUCKDUCKGO_SEARCH'):
        AVAILABLE_SOURCES[duckduckgo_searcher.SOURCE_NAME] = duckduckgo_searcher.search_duckduckgo
    if _get_boolean_env_var('ENABLE_ARXIV_SEARCH'):
        AVAILABLE_SOURCES[arxiv_fetcher.SOURCE_NAME] = arxiv_fetcher.fetch_arxiv_data
    if _get_boolean_env_var('ENABLE_PUBMED_SEARCH'):
        AVAILABLE_SOURCES[pubmed_fetcher.SOURCE_NAME] = pubmed_fetcher.fetch_articles_for_query
    if _get_boolean_env_var('ENABLE_PDF_API_1'):
        AVAILABLE_SOURCES[pdf_fetcher_1.SOURCE_NAME] = pdf_fetcher_1.fetch_pdf_data_1
    if _get_boolean_env_var('ENABLE_PDF_API_2'):
        AVAILABLE_SOURCES[pdf_fetcher_2.SOURCE_NAME] = pdf_fetcher_2.fetch_pdf_data_2
    if _get_boolean_env_var('ENABLE_PDF_API_3'):
        AVAILABLE_SOURCES[pdf_fetcher_3.SOURCE_NAME] = pdf_fetcher_3.fetch_pdf_data_3
    # Add other fetchers here in the same pattern

_initialize_sources()

def get_available_sources() -> List[str]:
    """Returns the list of available source names."""
    return list(AVAILABLE_SOURCES.keys())

def conduct_research(
    query: str,
    selected_data_sources: Set[str],
    uploaded_pdf_files: Optional[List[Union[io.BytesIO, Any]]] = None,
    pdf_types: Optional[Dict[str, str]] = None,
    max_pubmed_articles: int = 3,
    on_progress_update: Optional[Callable[[str], None]] = None,
    pdf_vector_store: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Conducts research based on a query and selected data sources.
    Implements multi-stage LLM processing for balanced source analysis.
    """
    
    def _progress(message: str):
        if on_progress_update:
            on_progress_update(message)
        print(message)

    # Initialize data structures dynamically
    source_data: Dict[str, List[Dict[str, Any]]] = {}
    
    processing_errors: List[str] = []

    _progress("Starting research process...")
    _progress(f"Query: {query}")
    _progress(f"Selected data sources: {', '.join(selected_data_sources)}")

    # 1. Process PDF sources (special case)
    if SOURCE_PDF in selected_data_sources and pdf_vector_store and pdf_vector_store.vector_store:
        _progress(f"Searching indexed PDF chunks for query: '{query}'...")
        source_data['pdf_sources'] = []
        try:
            relevant_pdf_chunks = pdf_vector_store.search_relevant_chunks(query, k=MAX_PDF_CHUNKS_TO_LLM)
            if relevant_pdf_chunks:
                _progress(f"Found {len(relevant_pdf_chunks)} relevant chunks from indexed PDFs.")
                
                # Filter chunks by PDF type if types are specified
                filtered_chunks = relevant_pdf_chunks
                if pdf_types and not uploaded_pdf_files:
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

    # 2. Process all other selected data sources dynamically
    for source_name, fetch_function in AVAILABLE_SOURCES.items():
        if source_name in selected_data_sources and fetch_function is not None:
            _progress(f"Fetching data from {source_name} for query: '{query}'...")
            if not query:
                _progress(f"Skipping {source_name} search as query is empty.")
                continue
            
            try:
                # Note: This part needs to be standardized. Assuming fetchers return a list of dicts.
                # This is a simplification and might need adjustment based on actual fetcher signatures.
                if source_name == pubmed_fetcher.SOURCE_NAME:
                     # Special handling for PubMed fetcher if its signature is different
                    results = fetch_function(query, max_articles=max_pubmed_articles)
                elif source_name == duckduckgo_searcher.SOURCE_NAME:
                    results = fetch_function(query, num_results=MAX_DUCKDUCKGO_RESULTS)
                else:
                    results = fetch_function(query, max_results=10) # A default for others

                if not results:
                    _progress(f"No results found from {source_name}.")
                    continue

                _progress(f"Found {len(results)} results from {source_name}.")
                
                # Determine the key for the source_data dictionary
                if source_name == duckduckgo_searcher.SOURCE_NAME:
                    source_key = 'web_sources'
                else:
                    # Generic key generation for other sources
                    source_key = source_name.lower().replace(' ', '_').replace('articles', '').replace('papers', '').strip().replace('__', '_') + '_sources'
                
                if source_key not in source_data:
                    source_data[source_key] = []

                # Standardize and append results
                for item in results:
                    # Handle variations in return formats (e.g. arxiv vs duckduckgo)
                    if isinstance(item, dict):
                        title = item.get('title', 'No title')
                        content = item.get('content', item.get('snippet', 'No content available'))
                        url = item.get('url', item.get('href', ''))
                        metadata = item.get('metadata', {})
                        
                        source_data[source_key].append({
                            'title': title,
                            'content': content,
                            'url': url,
                            'metadata': metadata
                        })
                    else:
                        _progress(f"Warning: Skipping non-dict item from {source_name}: {item}")

            except Exception as e:
                error_msg = f"Exception fetching from {source_name}: {str(e)}"
                _progress(error_msg)
                processing_errors.append(error_msg)

    # Pass the gathered data to the synthesis helper function
    return _perform_synthesis(query, source_data, processing_errors, _progress)

def _summarize_individual_sources(query: str, source_data: Dict[str, List], progress_callback) -> Dict[str, str]:
    """
    Stage 1: Summarize each source individually to prevent dominance.
    """
    source_summaries = {}
    
    # Process each source type
    for source_type, sources in source_data.items():
        if not sources:
            continue
            
        source_type_name = source_type.replace('_sources', '').replace('_', ' ').title()
        progress_callback(f"Summarizing {len(sources)} {source_type_name} sources...")
        
        # Combine all sources of this type
        combined_content = ""
        for i, source in enumerate(sources):
            combined_content += f"\n--- {source_type_name} Source {i+1} ---\n"
            combined_content += f"Title: {source.get('title', 'No title')}\n"
            combined_content += f"Content: {source.get('content', 'No content')}\n"
            if source.get('url'):
                combined_content += f"URL: {source.get('url')}\n"
            combined_content += "---\n"
        
        # Create summarization prompt
        summary_prompt = f"""
You are an expert research assistant. Your task is to summarize the key information from the following {source_type_name} sources related to this query:

Query: "{query}"

{source_type_name} Sources:
{combined_content}

Instructions:
1. Focus on information directly relevant to the query
2. Extract key facts, findings, and insights
3. Maintain objectivity and accuracy
4. Highlight any conflicting information within these sources
5. Keep the summary concise but comprehensive (aim for 200-400 words)
6. Note the type and reliability of the source material

Provide a clear, structured summary:
"""
        
        # Get summary from LLM
        try:
            summary_response = llm_handler.get_llm_response(summary_prompt)
            if not summary_response.startswith("Error:"):
                source_summaries[source_type] = summary_response
                progress_callback(f"✓ Completed summary for {source_type_name}")
            else:
                progress_callback(f"✗ Failed to summarize {source_type_name}: {summary_response}")
                source_summaries[source_type] = f"Error summarizing {source_type_name} sources."
        except Exception as e:
            progress_callback(f"✗ Exception summarizing {source_type_name}: {str(e)}")
            source_summaries[source_type] = f"Error summarizing {source_type_name} sources."
    
    return source_summaries

def _create_final_synthesis(query: str, source_summaries: Dict[str, str], progress_callback) -> str:
    """
    Stage 2: Create final synthesis from individual source summaries.
    """
    if not source_summaries:
        return "No source summaries available for synthesis."
    
    # Combine all source summaries
    combined_summaries = ""
    for source_type, summary in source_summaries.items():
        source_type_name = source_type.replace('_sources', '').replace('_', ' ').title()
        combined_summaries += f"\n--- {source_type_name} Summary ---\n{summary}\n---\n"
    
    # Create synthesis prompt
    synthesis_prompt = f"""
You are an expert research analyst. Your task is to create a comprehensive, balanced synthesis from the following source summaries to answer the user's query.

User's Query: "{query}"

Source Summaries:
{combined_summaries}

Instructions:
1. Create a balanced, comprehensive answer that draws from ALL source types equally
2. Ensure no single source type dominates the final conclusion
3. Identify areas of agreement and disagreement across sources
4. Highlight the strengths and limitations of different source types
5. Provide a well-structured, analytical response
6. Use clear headings and bullet points where appropriate
7. Acknowledge any gaps in the available information
8. Maintain objectivity and avoid bias toward any particular source type

Structure your response with:
- Executive Summary
- Key Findings (organized by theme)
- Source Analysis (strengths/limitations of each source type)
- Conclusions and Recommendations
- Areas for Further Research

Begin your synthesis:
"""
    
    progress_callback("Creating final synthesis from source summaries...")
    
    try:
        synthesis_response = llm_handler.get_llm_response(synthesis_prompt)
        if not synthesis_response.startswith("Error:"):
            progress_callback("✓ Final synthesis completed")
            return synthesis_response
        else:
            progress_callback(f"✗ Failed to create final synthesis: {synthesis_response}")
            return f"Error creating final synthesis: {synthesis_response}"
    except Exception as e:
        progress_callback(f"✗ Exception in final synthesis: {str(e)}")
        return f"Error creating final synthesis: {str(e)}"

def _create_final_report(query: str, final_synthesis: str, source_data: Dict[str, List], 
                        source_summaries: Dict[str, str], processing_errors: List[str]) -> str:
    """
    Create the final HTML report with multi-stage processing results.
    """
    # Count total sources
    total_sources = sum(len(sources) for sources in source_data.values())
    
    report = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px;">AI Research Report: "{query}"</h1>

<div style="background: #e8f5e8; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>🤖 Multi-Stage AI Synthesis:</strong> This report uses a two-stage AI process: individual source summarization followed by balanced synthesis to ensure no single source dominates the results.
</div>
"""
    
    # Source statistics
    if total_sources > 0:
        report += f"""
<h2 style="color: #34495e; margin-top: 30px;">📊 Sources Analyzed</h2>
<div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
<div style="font-weight: bold; margin-bottom: 10px;">Total Sources: {total_sources}</div>
"""
        for source_type, sources in source_data.items():
            if sources:
                source_type_name = source_type.replace('_sources', '').replace('_', ' ').title()
                report += f"<div style='margin: 5px 0;'>• {source_type_name}: {len(sources)} sources</div>"
        report += "</div>"
    
    # Individual source summaries
    if source_summaries:
        report += """
<h2 style="color: #34495e; margin-top: 30px;">📝 Individual Source Summaries</h2>
<div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0;">
"""
        for source_type, summary in source_summaries.items():
            source_type_name = source_type.replace('_sources', '').replace('_', ' ').title()
            report += f"""
<div style="margin: 20px 0; padding: 15px; background: white; border-radius: 5px; border-left: 4px solid #667eea;">
<h3 style="color: #2c3e50; margin-top: 0;">{source_type_name}</h3>
<div style="line-height: 1.6;">{summary}</div>
</div>
"""
        report += "</div>"
    
    # Processing errors
    if processing_errors:
        report += """
<h2 style="color: #e74c3c; margin-top: 30px;">⚠️ Processing Issues</h2>
<div style="background: #fdf2f2; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0;">
"""
        for err in processing_errors:
            report += f"<div style='margin: 8px 0; color: #c0392b;'>• {err}</div>"
        report += "</div>"
    
    # Final synthesis
    report += """
<hr style="margin: 30px 0; border: none; border-top: 2px solid #e1e8ed;">
<h2 style="color: #2c3e50; margin-top: 30px;">💡 Final AI Synthesis</h2>
<div style="background: white; border: 1px solid #e1e8ed; border-radius: 8px; padding: 25px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); line-height: 1.6; font-size: 1.1em;">
"""
    report += final_synthesis
    report += """
</div>
</div>
"""
    
    return report

def _create_raw_data_report(query: str, source_data: Dict[str, List], processing_errors: List[str]) -> Dict[str, Any]:
    """
    Create a report when LLM is not available.
    """
    total_sources = sum(len(sources) for sources in source_data.values())
    
    report = f"""
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px;">Research Report: "{query}"</h1>

<div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
<strong>ℹ️ Note:</strong> LLM processing is not available. Use the Source Management section below to view individual source excerpts and regenerate insights.
</div>
"""
    
    if processing_errors:
        report += """
<h2 style="color: #e74c3c; margin-top: 30px;">⚠️ Processing Issues</h2>
<div style="background: #fdf2f2; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0;">
"""
        for err in processing_errors:
            report += f"<div style='margin: 8px 0; color: #c0392b;'>• {err}</div>"
        report += "</div>"
    
    report += f"""
<hr style="margin: 30px 0; border: none; border-top: 2px solid #e1e8ed;">
<div style="background: #e8f5e8; border: 1px solid #c8e6c9; border-radius: 8px; padding: 15px; margin: 20px 0;">
    <strong>📊 Summary:</strong> {total_sources} sources were processed. Use the Source Management section below to view individual excerpts and regenerate insights from selected sources.
</div>
</div>
"""
    
    return {
        'report': report,
        'source_data': source_data,
        'is_raw_data': True
    }

def regenerate_report_from_sources(
    query: str,
    source_data: Dict[str, List[Dict[str, Any]]],
    on_progress_update: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """
    Regenerates a research report from a pre-existing, filtered set of source data.
    """
    def _progress(message: str):
        if on_progress_update:
            on_progress_update(message)
        print(message)

    _progress("Starting report regeneration from selected sources...")

    # The synthesis logic is the same, so we can reuse it.
    # We pass an empty list for processing_errors as we are not fetching new data.
    return _perform_synthesis(query, source_data, [], _progress)


def _perform_synthesis(
    query: str, 
    source_data: Dict[str, List[Dict[str, Any]]], 
    processing_errors: List[str], 
    progress_callback: Callable[[str], None]
) -> Dict[str, Any]:
    """
    Private helper to perform the synthesis part of the research,
    callable by both conduct_research and regenerate_report.
    """
    total_sources = sum(len(sources) for sources in source_data.values())
    if total_sources == 0:
        progress_callback("No text content available to synthesize.")
        return {
            'report': "No information was available to generate a report.",
            'source_data': source_data,
            'is_raw_data': True
        }

    progress_callback(f"Synthesizing information from {total_sources} distinct source entries.")

    # Check if LLM is available before processing
    progress_callback("Checking LLM availability...")
    llm_test_response = llm_handler.get_llm_response("Test", "You are a helpful assistant.")
    llm_available = not (llm_test_response.startswith("Error:") or "Azure OpenAI" in llm_test_response or "Language Model" in llm_test_response)
    
    if not llm_available:
        progress_callback("LLM is not available. Displaying raw data from each source separately.")
        return _create_raw_data_report(query, source_data, processing_errors)
    
    # LLM is available - proceed with multi-stage processing
    progress_callback("LLM is available. Proceeding with multi-stage synthesis...")
    
    # Stage 1: Individual source summarization
    progress_callback("Stage 1: Summarizing each source individually...")
    source_summaries = _summarize_individual_sources(query, source_data, progress_callback)
    
    # Stage 2: Final synthesis from source summaries
    progress_callback("Stage 2: Creating final synthesis from source summaries...")
    final_synthesis = _create_final_synthesis(query, source_summaries, progress_callback)
    
    # Create final report
    final_report = _create_final_report(query, final_synthesis, source_data, source_summaries, processing_errors)
    
    progress_callback("Synthesis process completed.")
    return {
        'report': final_report,
        'source_data': source_data,
        'is_raw_data': False
    }
