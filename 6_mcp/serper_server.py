#!/usr/bin/env python3
"""
Serper MCP Server

A Model Context Protocol server that provides web search capabilities using the Serper API.
"""

import os
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("serper_search")

@mcp.tool()
async def web_search(
    query: str, 
    num_results: int = 10, 
    country: str = "us"
) -> str:
    """Search the web using Serper API. Returns organic search results with titles, links, and snippets.
    
    Args:
        query: The search query to execute
        num_results: Number of results to return (default: 10, max: 100)
        country: Country code for localized results (e.g., 'us', 'uk', 'ca')
    """
    # Get API key from environment
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY environment variable is not set. Please get your API key from https://serper.dev/"
    
    if not query:
        return "Error: Query parameter is required"
    
    # Limit num_results to reasonable bounds
    num_results = max(1, min(num_results, 100))
    
    try:
        # Make request to Serper API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "num": num_results,
                    "gl": country
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                return f"Error: Serper API returned status {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Format results
            results = []
            organic_results = data.get("organic", [])
            
            for i, result in enumerate(organic_results[:num_results], 1):
                results.append(f"{i}. **{result.get('title', 'No title')}**")
                results.append(f"   Link: {result.get('link', 'No link')}")
                results.append(f"   Snippet: {result.get('snippet', 'No snippet')}")
                results.append("")
            
            # Add search information
            search_info = data.get("searchInformation", {})
            total_results = search_info.get("totalResults", "Unknown")
            search_time = search_info.get("searchTime", "Unknown")
            
            formatted_results = f"# Search Results for: {query}\n\n"
            formatted_results += f"**Search Information:**\n"
            formatted_results += f"- Total Results: {total_results}\n"
            formatted_results += f"- Search Time: {search_time} seconds\n"
            formatted_results += f"- Country: {country.upper()}\n\n"
            formatted_results += "**Results:**\n\n"
            formatted_results += "\n".join(results)
            
            return formatted_results
            
    except httpx.TimeoutException:
        return "Error: Request to Serper API timed out"
    except httpx.RequestError as e:
        return f"Error: Request to Serper API failed: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error occurred: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')