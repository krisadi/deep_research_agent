"""
PDF Fetcher 2 - External API Integration
Fetches indexed PDF data from external API endpoint 2
"""

import os
from typing import List, Dict, Any

SOURCE_NAME = "pdf_fetcher_2"

def fetch_pdfs(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch PDF documents from external API (currently returns dummy data).
    """
    # Check if this source is enabled
    if not _get_boolean_env_var('ENABLE_PDF_FETCHER_2'):
        return []
    
    # Return dummy data for testing
    dummy_results = [
        {
            'title': f'Academic Paper: {query}',
            'url': 'https://example.com/academic-paper.pdf',
            'content': f'This dummy academic paper presents research findings on "{query}". It includes abstract, introduction, methodology, results, discussion, and conclusion sections. The paper follows standard academic formatting and citation practices.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Industry Report: {query} Market Analysis',
            'url': 'https://example.com/industry-report.pdf',
            'content': f'An industry report analyzing the market trends and opportunities related to "{query}". This document provides market size estimates, growth projections, competitive landscape analysis, and strategic recommendations for stakeholders.',
            'source': SOURCE_NAME
        },
        {
            'title': f'White Paper: {query} Implementation Guide',
            'url': 'https://example.com/white-paper.pdf',
            'content': f'A comprehensive white paper providing implementation guidance for "{query}". This document covers best practices, step-by-step procedures, case studies, and troubleshooting tips for successful deployment.',
            'source': SOURCE_NAME
        },
        {
            'title': f'Case Study: {query} Success Story',
            'url': 'https://example.com/case-study.pdf',
            'content': f'This case study documents a successful implementation of "{query}" in a real-world scenario. It details the challenges faced, solutions implemented, results achieved, and lessons learned for future projects.',
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
    test_query = "artificial intelligence research"
    print(f"Testing {SOURCE_NAME} with query: '{test_query}'")
    
    results = fetch_pdfs(test_query, max_results=3)
    
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {result.get('title')}")
        print(f"Content: {result.get('content', '')[:200]}...")
        print(f"URL: {result.get('url')}")
        print(f"Source: {result.get('source')}") 