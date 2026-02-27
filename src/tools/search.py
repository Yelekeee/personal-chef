from langchain_community.tools.tavily_search import TavilySearchResults


def get_search_tools() -> list:
    """Return the list of tools available to the research agent."""
    return [TavilySearchResults(max_results=3)]
