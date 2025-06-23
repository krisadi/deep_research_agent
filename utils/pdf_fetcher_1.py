"""
PDF Fetcher 1 - External API Integration
Fetches indexed PDF data from external API endpoint 1
"""

import requests
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SOURCE_NAME = "Indexed PDFs - API 1"

def fetch_pdf_data_1(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch indexed PDF data from external API endpoint 1
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of PDF documents with metadata
    """
    # Get API configuration from environment variables
    api_endpoint = os.getenv("PDF_API_1_ENDPOINT")
    api_key = os.getenv("PDF_API_1_KEY")
    
    if not api_endpoint:
        print(f"Warning: PDF_API_1_ENDPOINT not configured for {SOURCE_NAME}")
        return []
    
    try:
        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        }
        
        payload = {
            "query": query,
            "max_results": max_results,
            "include_content": True
        }
        
        # Make the API call
        response = requests.post(
            api_endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Standardize the response format
            standardized_results = []
            for item in data.get("results", []):
                standardized_results.append({
                    'title': item.get('title', 'No title'),
                    'content': item.get('content', item.get('text', 'No content available')),
                    'url': item.get('url', item.get('source_url', '')),
                    'metadata': {
                        'source': 'PDF_API_1',
                        'pdf_id': item.get('id', ''),
                        'file_name': item.get('file_name', ''),
                        'page_number': item.get('page_number', ''),
                        'confidence_score': item.get('confidence_score', ''),
                        'extracted_date': item.get('extracted_date', '')
                    }
                })
            
            print(f"Fetched {len(standardized_results)} results from {SOURCE_NAME}")
            return standardized_results
            
        else:
            print(f"Error fetching from {SOURCE_NAME}: HTTP {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching from {SOURCE_NAME}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching from {SOURCE_NAME}: {e}")
        return []

if __name__ == '__main__':
    # Test the fetcher
    test_query = "machine learning applications"
    print(f"Testing {SOURCE_NAME} with query: '{test_query}'")
    
    results = fetch_pdf_data_1(test_query, max_results=3)
    
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {result.get('title')}")
        print(f"Content: {result.get('content', '')[:200]}...")
        print(f"URL: {result.get('url')}")
        print(f"Metadata: {result.get('metadata')}") 