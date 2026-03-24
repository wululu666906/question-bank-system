import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo and return a list of top results.
    Each result is a dictionary with 'title', 'href', and 'body'.
    """
    logger.info(f"Searching web for: {query}")
    try:
        results = []
        with DDGS() as ddgs:
            # text() returns an iterator of dicts: {'title': ..., 'href': ..., 'body': ...}
            for r in ddgs.text(query, max_results=max_results):
                results.append(r)
        logger.info(f"Found {len(results)} results.")
        return results
    except Exception as e:
        logger.error(f"Error during web search: {e}")
        return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = search_web("高中物理牛顿三定律结合应用", 3)
    for r in res:
        print(r)
