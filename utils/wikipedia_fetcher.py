"""
Wikipedia data fetcher for research queries.
Fetches Wikipedia articles and summaries
"""

import requests
from typing import Dict, List, Any
import re
import urllib.parse

SOURCE_NAME = "Wikipedia Articles"

def fetch_wikipedia_data(query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Fetch Wikipedia data based on a query.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        **kwargs: Additional parameters (language, etc.)
    
    Returns:
        dict: Standardized JSON response
    """
    try:
        # Wikipedia API endpoint for search
        search_url = "https://en.wikipedia.org/w/api.php"
        
        # Search for relevant pages
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': min(max_results, 50),
            'srnamespace': 0,  # Main namespace only
            'srprop': 'snippet|title|pageid'  # Get snippet, title, and page ID
        }
        
        # Make search request
        search_response = requests.get(search_url, params=search_params, timeout=30)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        # Extract search results
        data = []
        search_results = search_data.get('query', {}).get('search', [])
        
        for result in search_results:
            try:
                # Get page info from search result
                page_title = result.get('title', '')
                page_id = result.get('pageid', '')
                snippet = result.get('snippet', '')
                
                if not page_title or not page_id:
                    continue
                
                # Clean up snippet (remove HTML tags)
                clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                clean_snippet = re.sub(r'&[^;]+;', ' ', clean_snippet)  # Remove HTML entities
                clean_snippet = clean_snippet.strip()
                
                # Create URL for the page
                encoded_title = urllib.parse.quote(page_title.replace(' ', '_'))
                url = f"https://en.wikipedia.org/wiki/{encoded_title}"
                
                # Create metadata
                metadata = {
                    "authors": [],  # Wikipedia articles don't have individual authors
                    "date": "Ongoing",  # Wikipedia is continuously updated
                    "type": "encyclopedia_article",
                    "source": "Wikipedia",
                    "page_id": page_id,
                    "page_type": "article"
                }
                
                data.append({
                    "title": page_title,
                    "content": clean_snippet,
                    "url": url,
                    "metadata": metadata
                })
                
            except Exception as e:
                # Skip individual page errors and continue
                continue
        
        return {
            "success": True,
            "source_name": "Wikipedia",
            "query": query,
            "data": data,
            "error": None,
            "count": len(data)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "source_name": "Wikipedia",
            "query": query,
            "data": [],
            "error": f"Network error: {str(e)}",
            "count": 0
        }
    except Exception as e:
        return {
            "success": False,
            "source_name": "Wikipedia",
            "query": query,
            "data": [],
            "error": f"Unexpected error: {str(e)}",
            "count": 0
        } 