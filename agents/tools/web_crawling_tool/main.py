import os
import requests
from serpapi import SerpApiClient
from bs4 import BeautifulSoup

# Set a limit for the number of search results to process
SEARCH_RESULT_LIMIT = 3
# Set a limit for the content length from each page
CONTENT_CHAR_LIMIT = 2000

def main(params):
    query = params.get("query")
    api_key = os.environ.get("API_KEY")

    if not query:
        return {"statusCode": 400, "body": {"error": "A 'query' parameter is required."}}
    if not api_key:
        return {"statusCode": 500, "body": {"error": "API_KEY secret is not configured."}}

    print(f"Received query: {query}")
    scraped_data = []

    try:
        search_params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
        }
        client = SerpApiClient(search_params)
        results = client.get_dict()
        
        # --- DEBUGGING LINES ---
        print(f"SerpApi raw response: {results}") # <-- ADD THIS LINE to see the full response
        
        # --- ROBUSTNESS CHECK ---
        # <-- ADD THIS BLOCK to handle API errors gracefully
        if "organic_results" not in results:
            api_error = results.get("error", "No organic_results found in API response.")
            print(f"API Error: {api_error}")
            return {"statusCode": 500, "body": {"error": f"Search API Error: {api_error}"}}
        # ------------------------

        links = [r['link'] for r in results.get("organic_results", [])[:SEARCH_RESULT_LIMIT]]
        print(f"Found {len(links)} results via SerpApi.")

        for url in links:
            try:
                response = requests.get(url, timeout=10, headers={'User-Agent': 'watsonx-crawler-bot/1.0'})
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'lxml')
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                text_content = soup.get_text(separator=' ', strip=True)
                truncated_content = text_content[:CONTENT_CHAR_LIMIT]
                scraped_data.append({"source": url, "content": truncated_content})
                print(f"Successfully scraped: {url}")
            except requests.RequestException as e:
                print(f"Could not fetch or read URL {url}: {e}")
                continue

    except Exception as e:
        print(f"An error occurred during search or scraping: {e}")
        return {"statusCode": 500, "body": {"error": f"An internal error occurred: {str(e)}"}}

    final_summary = " ".join([data['content'] for data in scraped_data])
    return {
        "statusCode": 200,
        "body": {
            "summary": final_summary,
            "sources": [data['source'] for data in scraped_data]
        }
    }