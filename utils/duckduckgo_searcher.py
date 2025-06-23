# This module will contain functions to interact with DuckDuckGo search.
from duckduckgo_search import DDGS
from typing import List, Dict, Optional

SOURCE_NAME = "DuckDuckGo Search"

def search_duckduckgo(query: str, num_results: int = 5, region: str = 'wt-wt') -> List[Dict[str, str]]:
    """
    Performs a DuckDuckGo search and returns formatted results.

    Args:
        query (str): The search query.
        num_results (int): The maximum number of results to return.
        region (str): The region to search in, e.g., 'us-en', 'uk-en', 'wt-wt' (world-wide).

    Returns:
        List[Dict[str, str]]: A list of dictionaries, where each dictionary
                              contains 'title', 'url' (href), and 'snippet' (body)
                              for a search result. Returns an empty list on error.
    """
    results = []
    if not query:
        return results

    try:
        print(f"Performing DuckDuckGo search for: '{query}', num_results={num_results}, region='{region}'")
        # DDGS().text returns a generator of dictionaries
        with DDGS() as ddgs:
            ddgs_results = ddgs.text(
                keywords=query,
                region=region,
                safesearch='moderate', # Or 'on', 'off'
                max_results=num_results
            )
            
            if ddgs_results:
                for i, r in enumerate(ddgs_results):
                    if i >= num_results: # ddgs.text might yield more than max_results sometimes
                        break
                    results.append({
                        "title": r.get("title", "N/A"),
                        "url": r.get("href", "#"),
                        "snippet": r.get("body", "N/A")
                    })
        print(f"DuckDuckGo search returned {len(results)} results.")
        return results
    except Exception as e:
        print(f"Error during DuckDuckGo search for query '{query}': {e}")
        return [] # Return empty list on error

if __name__ == '__main__':
    # Test the search function
    test_query = "benefits of green tea"
    print(f"\nTesting DuckDuckGo search with query: '{test_query}'")
    search_results = search_duckduckgo(test_query, num_results=3)

    if search_results:
        print(f"\nFound {len(search_results)} results:")
        for i, result in enumerate(search_results):
            print(f"\nResult {i+1}:")
            print(f"  Title: {result['title']}")
            print(f"  URL: {result['url']}")
            print(f"  Snippet: {result['snippet']}")
    else:
        print("No results found or an error occurred.")

    test_query_empty = ""
    print(f"\nTesting DuckDuckGo search with empty query: '{test_query_empty}'")
    search_results_empty = search_duckduckgo(test_query_empty, num_results=3)
    if not search_results_empty:
        print("Correctly returned empty list for empty query.")
    else:
        print(f"Error: Expected empty list for empty query, got {len(search_results_empty)} results.")
