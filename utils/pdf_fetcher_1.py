"""
PDF Fetcher 1 - External API Integration
Fetches indexed PDF data from external API endpoint 1
"""

import os
from typing import List, Dict, Any

SOURCE_NAME = "pdf_fetcher_1"

def fetch_pdfs(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch PDF documents from external API (currently returns dummy data).
    """
    # Check if this source is enabled
    if not _get_boolean_env_var('ENABLE_PDF_FETCHER_1'):
        return []
    
    # Return dummy data for testing
    dummy_results = [
        {
            'title': f'Dummy PDF Document 1: {query}',
            'url': 'https://example.com/dummy-pdf-1.pdf',
            'content': f'This is dummy content for PDF document 1 related to "{query}". It contains sample text that would normally be extracted from a PDF file. This document discusses various aspects of the topic and provides preliminary findings.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Research Paper on {query}',
            'url': 'https://example.com/research-paper.pdf',
            'content': f'This dummy research paper explores the topic of "{query}" in detail. It includes methodology, results, and conclusions. The paper presents findings from various studies and provides insights into current research trends.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Technical Report: {query} Analysis',
            'url': 'https://example.com/technical-report.pdf',
            'content': f'A comprehensive technical report analyzing "{query}". This document provides detailed technical specifications, implementation details, and performance metrics. It serves as a reference for practitioners in the field.',
            'source': SOURCE_NAME
        }
    ]
    
    # Limit to max_results
    return dummy_results[:max_results]

def _get_boolean_env_var(var_name: str) -> bool:
    """Helper function to get boolean environment variables."""
    return os.getenv(var_name, 'false').lower() in ('true', '1', 'yes', 'on')

if __name__ == '__main__':
    # Test the fetcher
    test_query = "machine learning applications"
    print(f"Testing {SOURCE_NAME} with query: '{test_query}'")
    
    results = fetch_pdfs(test_query, max_results=3)
    
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {result.get('title')}")
        print(f"Content: {result.get('content', '')[:200]}...")
        print(f"URL: {result.get('url')}")
        print(f"Source: {result.get('source')}") 