from typing import Any
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
import asyncio
from config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID


# Initialize FastMCP server
mcp = FastMCP("search", log_level="ERROR")



def fetch_full_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text, e.g., from paragraph tags
        return ' '.join([p.get_text() for p in soup.find_all('p')])
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
def search_google(query: str, domains: list[str] = None) -> str:
    """Search Google for a query, optionally restricted to specific domains.

    Args:
        query (str): The search query.
        domains (list[str], optional): A list of domains to restrict the search to (e.g., ["example.com", "another.com"]).

    Returns:
        str: Full text of the search results.
    """
    # Add domain restrictions to the query if provided
    if domains:
        domain_query = " OR ".join([f"site:{domain}" for domain in domains])
        query = f"({domain_query}) {query}"

    # Build the service
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

    raw_results = service.cse().list(q=query, cx=GOOGLE_SEARCH_ENGINE_ID, num=10).execute()
    search_results = [
        {
            'title': item['title'],
            'link': item['link'],
            'snippet': item['snippet'],
            'full_text': fetch_full_text(item['link'])  # Fetch full text from the link
        }
        for item in raw_results.get('items', [])
    ]
    return "\n---\n".join([search_result['full_text'] for search_result in search_results])

@mcp.tool()
def search_sac_cac(query: str) -> str:
    """Search Google for a query, specifically for the SAC CAC domain.

    Args:
        query (str): The search query.

    Returns:
        str: Full text of the search results.
    """
    return search_google(query, domains=["https://support.atlassian.com", "https://confluence.atlassian.com/"])

if __name__ == "__main__":
    mcp.run(transport='stdio')