"""
arXiv data fetcher for research queries.
Fetches academic papers from arXiv.org
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import time

SOURCE_NAME = "arXiv Papers"

def fetch_arxiv_data(query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Fetch data from arXiv based on a query.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        **kwargs: Additional parameters (ignored for arXiv)
    
    Returns:
        dict: Standardized JSON response
    """
    try:
        # arXiv API endpoint
        base_url = "http://export.arxiv.org/api/query"
        
        # Prepare query parameters
        params = {
            'search_query': f'all:"{query}"',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        # Make request to arXiv API
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Extract namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Parse entries
        data = []
        entries = root.findall('.//atom:entry', ns)
        
        for entry in entries:
            # Extract title
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No title"
            
            # Extract summary/abstract
            summary_elem = entry.find('atom:summary', ns)
            content = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else "No abstract available"
            
            # Extract URL
            id_elem = entry.find('atom:id', ns)
            url = id_elem.text if id_elem is not None else ""
            
            # Extract authors
            authors = []
            author_elems = entry.findall('.//atom:name', ns)
            for author_elem in author_elems:
                if author_elem.text:
                    authors.append(author_elem.text.strip())
            
            # Extract publication date
            published_elem = entry.find('atom:published', ns)
            date = published_elem.text[:10] if published_elem is not None and published_elem.text else "Unknown date"
            
            # Extract categories
            categories = []
            category_elems = entry.findall('.//atom:category', ns)
            for cat_elem in category_elems:
                scheme = cat_elem.get('term')
                if scheme:
                    categories.append(scheme)
            
            # Create metadata
            metadata = {
                "authors": authors,
                "date": date,
                "type": "academic_paper",
                "categories": categories,
                "source": "arXiv"
            }
            
            data.append({
                "title": title,
                "content": content,
                "url": url,
                "metadata": metadata
            })
        
        return {
            "success": True,
            "source_name": "arXiv",
            "query": query,
            "data": data,
            "error": None,
            "count": len(data)
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "source_name": "arXiv",
            "query": query,
            "data": [],
            "error": f"Network error: {str(e)}",
            "count": 0
        }
    except ET.ParseError as e:
        return {
            "success": False,
            "source_name": "arXiv",
            "query": query,
            "data": [],
            "error": f"XML parsing error: {str(e)}",
            "count": 0
        }
    except Exception as e:
        return {
            "success": False,
            "source_name": "arXiv",
            "query": query,
            "data": [],
            "error": f"Unexpected error: {str(e)}",
            "count": 0
        } 