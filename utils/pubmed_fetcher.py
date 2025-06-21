from Bio import Entrez, Medline
import os

# Always provide your email to NCBI
Entrez.email = os.getenv("NCBI_EMAIL", "your_email@example.com") # Set a default or use an env var

def search_pubmed(query, max_results=10):
    """
    Searches PubMed for articles based on keywords.
    
    Args:
        query (str): The search query or keywords.
        max_results (int): Maximum number of article IDs to fetch.
        
    Returns:
        list: A list of PubMed article IDs (PMIDs).
              Returns an empty list if the search fails or no articles are found.
    """
    if not Entrez.email or Entrez.email == "your_email@example.com":
        print("Warning: NCBI_EMAIL environment variable not set or using default. Please set it to your email address for PubMed API access.")
        # Optionally, you could prevent the call or return an error here.
        # For now, it will proceed but NCBI might block if abused.

    try:
        print(f"Searching PubMed for: '{query}', max_results={max_results}")
        handle = Entrez.esearch(db="pubmed", term=query, retmax=str(max_results), sort="relevance")
        record = Entrez.read(handle)
        handle.close()
        return record.get("IdList", [])
    except Exception as e:
        print(f"Error searching PubMed for query '{query}': {e}")
        return []

def fetch_article_details_batch(pmids):
    """
    Fetches details (e.g., abstract, title, authors) for a list of PubMed IDs using Medline format.
    
    Args:
        pmids (list): A list of PubMed IDs (strings).
        
    Returns:
        list: A list of dictionaries, where each dictionary contains article details 
              (e.g., {'pmid': ..., 'title': ..., 'abstract': ..., 'authors': ...}).
              Returns an empty list if fetching fails or no valid data is parsed.
    """
    if not pmids:
        return []
    if not Entrez.email or Entrez.email == "your_email@example.com":
        print("Warning: NCBI_EMAIL environment variable not set for fetching details.")
        # Potentially return early or raise an error.
        
    try:
        print(f"Fetching details for PubMed IDs: {', '.join(pmids)}")
        handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline", retmode="text")
        records = Medline.parse(handle)
        
        articles_details = []
        for record in records:
            # Medline parser returns a dictionary-like object
            pmid = record.get("PMID", "")
            title = record.get("TI", "N/A") # Title
            abstract = record.get("AB", "N/A") # Abstract
            authors = record.get("AU", []) # Authors (list)
            journal = record.get("JT", "N/A") # Journal Title
            
            articles_details.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal
            })
        handle.close()
        return articles_details
    except Exception as e:
        print(f"Error fetching details for PMIDs {', '.join(pmids)}: {e}")
        return []

def fetch_articles_for_query(query, max_articles=5):
    """
    Searches PubMed for a query and fetches details for a specified number of articles.

    Args:
        query (str): The search query.
        max_articles (int): The maximum number of articles to fetch details for.

    Returns:
        list: A list of dictionaries, where each dictionary contains details of an article.
    """
    if not query:
        return []
        
    print(f"Fetching articles for query: '{query}', max_articles={max_articles}")
    pmids = search_pubmed(query, max_results=max_articles)
    if not pmids:
        print(f"No PubMed IDs found for query: '{query}'")
        return []
    
    articles_data = fetch_article_details_batch(pmids)
    
    # The number of results from fetch_article_details_batch might be less than len(pmids)
    # if some IDs were invalid or data was missing.
    # max_articles is already handled by search_pubmed's retmax and the batch fetch.
    
    print(f"Fetched {len(articles_data)} article details for query: '{query}'")
    return articles_data

if __name__ == '__main__':
    # Simple test
    # To run this: python -m utils.pubmed_fetcher
    # Make sure NCBI_EMAIL is set in your environment, or update the default in Entrez.email
    
    test_query = "crispr gene editing"
    print(f"Running test with query: '{test_query}'")
    
    # Test search_pubmed
    ids = search_pubmed(test_query, max_results=2)
    print(f"Search results (PMIDs): {ids}")
    
    if ids:
        # Test fetch_article_details_batch
        details = fetch_article_details_batch(ids)
        for i, article in enumerate(details):
            print(f"\n--- Article {i+1} (PMID: {article.get('pmid')}) ---")
            print(f"  Title: {article.get('title')}")
            print(f"  Authors: {', '.join(article.get('authors', []))}")
            print(f"  Journal: {article.get('journal')}")
            print(f"  Abstract: {(article.get('abstract') or 'N/A')[:200]}...") # Print first 200 chars of abstract
    else:
        print("No articles found to fetch details for.")

    print("\n--- Test with fetch_articles_for_query ---")
    all_details = fetch_articles_for_query("covid vaccine efficacy", max_articles=2)
    for i, article in enumerate(all_details):
        print(f"\n--- Combined Fetch Article {i+1} (PMID: {article.get('pmid')}) ---")
        print(f"  Title: {article.get('title')}")
        print(f"  Abstract: {(article.get('abstract') or 'N/A')[:200]}...")
    
    if not all_details:
        print("No articles found via fetch_articles_for_query.")
