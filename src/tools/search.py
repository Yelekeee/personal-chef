from langchain_tavily import TavilySearch


def get_search_tools() -> list:
    """Return the list of tools available to the research agent."""
    return [TavilySearch(max_results=3)]
