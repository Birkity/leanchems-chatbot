import os
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

def search_web(query):
    """
    Search the web for up-to-date content and examples related to the user's idea.
    Returns a concise summary to add credibility and context.
    """
    try:
        with DDGS() as ddgs:
            # Flexible query: user's idea + keywords for examples and trends
            full_query = f"{query} real-world examples latest trends"
            logger.info(f"Searching web for: {full_query}")
            results = ddgs.text(full_query, max_results=10)  # More results for better coverage
            snippets = [result.get("body", "") for result in results if result.get("body")]
            
            if not snippets:
                logger.debug("No web results found.")
                return "No relevant web insights found at this time."
            
            # Summarize top results into a concise paragraph
            summary = " ".join(snippets[:3])[:700] + "..."  # Limit length for brevity
            logger.debug(f"Web search summary: {summary}")
            return f"**Web Insights**: {summary}"
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return "Unable to fetch web insights at this time."