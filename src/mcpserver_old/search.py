
from typing import Any
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
import asyncio
from src.config.config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID


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
    
@mcp.tool()
def search_google(query: str) -> str:
    """Search google for a query.

    Args:
        query (str): The search query. 
    """

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



if __name__ == "__main__":
    # Initialize and run the server
    # query = "Python programming"
    # search_results = search_google(query)

    # for item in search_results:
    #     print(f"Title: {item['title']}")
    #     print(f"Link: {item['link']}")
    #     print(f"Snippet: {item['snippet']}")
    #     print(f"Full Text: {item['full_text']}")
    #     print("-" * 20)
    mcp.run(transport='stdio')
