"""
PDF Fetcher 3 - External API Integration
Fetches indexed PDF data from external API endpoint 3
"""

import os
from typing import List, Dict, Any

SOURCE_NAME = "pdf_fetcher_3"

def fetch_pdfs(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch PDF documents from external API (currently returns dummy data).
    """
    # Check if this source is enabled
    if not _get_boolean_env_var('ENABLE_PDF_FETCHER_3'):
        return []
    
    # Return dummy data for testing
    dummy_results = [
        {
            'title': f'Conference Paper: {query}',
            'url': 'https://example.com/conference-paper.pdf',
            'content': f'This dummy conference paper presents research on "{query}" at a major academic conference. It includes peer-reviewed findings, experimental results, and contributions to the field. The paper follows conference submission guidelines.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Technical Documentation: {query}',
            'url': 'https://example.com/technical-docs.pdf',
            'content': f'Comprehensive technical documentation for "{query}". This document provides detailed specifications, API references, configuration guides, and troubleshooting information for developers and system administrators.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Research Brief: {query} Overview',
            'url': 'https://example.com/research-brief.pdf',
            'content': f'A concise research brief summarizing key findings and insights related to "{query}". This document provides executive summaries, key takeaways, and actionable recommendations for decision-makers.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Survey Paper: {query} Literature Review',
            'url': 'https://example.com/survey-paper.pdf',
            'content': f'A comprehensive survey paper reviewing the literature on "{query}". This document analyzes existing research, identifies trends, gaps, and future research directions in the field.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Policy Document: {query} Guidelines',
            'url': 'https://example.com/policy-document.pdf',
            'content': f'Policy guidelines and recommendations related to "{query}". This document outlines best practices, regulatory considerations, and compliance requirements for organizations implementing related solutions.',
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
    test_query = "data science methodologies"
    print(f"Testing {SOURCE_NAME} with query: '{test_query}'")
    
    results = fetch_pdfs(test_query, max_results=3)
    
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {result.get('title')}")
        print(f"Content: {result.get('content', '')[:200]}...")
        print(f"URL: {result.get('url')}")
        print(f"Source: {result.get('source')}") 