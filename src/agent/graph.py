from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import ResearchState
from src.tools.search import get_search_tools

load_dotenv()

SYSTEM_PROMPT = """You are a Personal Research Assistant. Your job is to help users \
research topics thoroughly and accurately.

When answering questions:
- Use the search tool to find up-to-date information when needed
- Synthesize information from multiple sources when available
- Be concise but comprehensive
- Cite key facts and indicate when information may be outdated
- If an image is provided, analyze it and incorporate your observations into the answer

You have access to a web search tool. Use it proactively for factual questions, \
current events, or any topic where up-to-date information matters."""


def build_graph():
    """Build and compile the ReAct research agent graph.

    Concepts demonstrated:
    - Foundational Models: ChatOpenAI with SystemMessage
    - Tools: TavilySearchResults bound via bind_tools + ToolNode
    - Short-term Memory: MemorySaver checkpointer keyed by thread_id
    - Multimodal: HumanMessage with image_url content blocks (handled in main.py)
    """
    # Foundational Models concept: configure the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Tools concept: get tools and bind them to the LLM
    tools = get_search_tools()
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: ResearchState) -> dict:
        """Invoke the LLM with the full conversation history plus system prompt."""
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Build the ReAct graph
    graph = StateGraph(ResearchState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")

    # tools_condition: routes to "tools" if the LLM made tool calls, else END
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    # Short-term Memory concept: MemorySaver persists state per thread_id
    return graph.compile(checkpointer=MemorySaver())
