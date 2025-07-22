"""Web search and webpage visiting tools for the multi-agent system."""

import re
from urllib.parse import urlparse

import requests
from smolagents import tool


@tool
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """
    Search DuckDuckGo for information and return a list of results.

    Args:
        query: Search query string (e.g., "Python programming tutorial")
        max_results: Maximum number of search results to return (1-10)

    Returns:
        A formatted string containing search results with titles, URLs, and snippets.
    """
    print(f"🔍 Searching DuckDuckGo for: {query}")

    try:
        # Validate max_results
        if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
            raise ValueError("max_results must be an integer between 1 and 10")

        # Simple DuckDuckGo instant answer API (no key required)
        # Note: This is a basic implementation. A production version would use
        # a more robust API like the official DuckDuckGo API or web scraping
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []

        # Add abstract if available
        if data.get("Abstract"):
            results.append(f"📄 **Summary**: {data['Abstract']}")
            if data.get("AbstractURL"):
                results.append(f"🔗 **Source**: {data['AbstractURL']}")

        # Add related topics
        if data.get("RelatedTopics"):
            results.append("\n📌 **Related Topics**:")
            for i, topic in enumerate(data["RelatedTopics"][:max_results]):
                if (
                    isinstance(topic, dict)
                    and topic.get("Text")
                    and topic.get("FirstURL")
                ):
                    results.append(f"{i + 1}. {topic['Text']}")
                    results.append(f"   🔗 {topic['FirstURL']}")

        # If no results from instant answers, return a message
        if not results:
            results.append(f"No instant answers found for '{query}'. ")
            results.append(
                "For comprehensive web search, try using a different search tool or visit search engines directly."
            )

        formatted_results = "\n".join(results)
        print(f"✅ Found search results for: {query}")
        return formatted_results

    except requests.RequestException as e:
        error_msg = f"Search request failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg) from e


@tool
def visit_webpage(url: str, max_chars: int = 8000) -> str:
    """
    Visit a webpage and extract its text content for analysis.

    Args:
        url: The URL to visit (e.g., "https://example.com/article")
        max_chars: Maximum number of characters to return (500-15000)

    Returns:
        Extracted text content from the webpage, cleaned and formatted.
    """
    print(f"🌐 Visiting webpage: {url}")

    try:
        # Validate inputs
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        if not isinstance(max_chars, int) or max_chars < 500 or max_chars > 15000:
            raise ValueError("max_chars must be an integer between 500 and 15000")

        # Validate URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("URL must include protocol (http:// or https://)")

        # Set headers to appear as a regular browser
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        # Make the request
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Simple text extraction (basic HTML parsing)
        content = response.text

        # Remove script and style elements
        content = re.sub(
            r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        content = re.sub(
            r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL | re.IGNORECASE
        )

        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)

        # Clean up whitespace
        content = re.sub(r"\s+", " ", content)
        content = content.strip()

        # Extract title if possible
        title_match = re.search(
            r"<title[^>]*>([^<]+)</title>", response.text, re.IGNORECASE
        )
        title = title_match.group(1).strip() if title_match else "No title found"

        # Truncate content if too long
        if len(content) > max_chars:
            content = content[:max_chars] + "... [Content truncated]"

        # Format the response
        result = f"📄 **Title**: {title}\n🔗 **URL**: {url}\n\n**Content**:\n{content}"

        print(f"✅ Successfully extracted content from: {url}")
        return result

    except requests.RequestException as e:
        error_msg = f"Failed to visit webpage {url}: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"Error processing webpage {url}: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg) from e


# Create tool classes for compatibility with smolagents factory pattern
class DuckDuckGoSearchTool:
    """DuckDuckGo search tool wrapper."""

    def __init__(self):
        self.name = "duckduckgo_search"
        self.description = duckduckgo_search.__doc__

    def __call__(self, *args, **kwargs):
        return duckduckgo_search(*args, **kwargs)


class VisitWebpageTool:
    """Webpage visiting tool wrapper."""

    def __init__(self):
        self.name = "visit_webpage"
        self.description = visit_webpage.__doc__

    def __call__(self, *args, **kwargs):
        return visit_webpage(*args, **kwargs)
