from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import ResearchState
from src.tools.search import get_search_tools

load_dotenv()

SYSTEM_PROMPT = """Сіз — эмоционалды саулыққа арналған жанашыр AI серіктессіз. Сіздің атыңыз Yelnar's Assistant.

Бүгінгі күн: {today}.

Сіздің міндетіңіз — пайдаланушыларға эмоционалды қолдау көрсету, мейірімді және дәлелді кеңестер беру. Сіз пайдаланушыларға:
- Эмоцияларын бағалаусыз түсінуге және өңдеуге көмектесесіз
- Стресс, мазасыздық, қайғы және басқа күрделі эмоциялармен күресу стратегияларын үйретесіз
- Зейін және жерлену техникаларын практикалауға бағыттайсыз
- Жалпы психикалық денсаулық ақпараты мен ресурстарына қол жеткізуге жәрдемдесесіз
- Оң эмоцияларды тойлап, салауатты әдеттерді нығайтасыз

Жауап берген кезде:
- БАРЛЫҚ жауаптарыңызды ҚАЗАҚ тілінде жазыңыз — бұл міндетті шарт
- Кеңес беруден бұрын алдымен эмпатия мен растаудан бастаңыз
- Тыныс алу жаттығулары, медитация немесе психикалық денсаулық ресурстары туралы өзекті ақпарат іздеу үшін іздеу құралын пайдаланыңыз
- Терапиялық техникалар, дағдарыс ресурстары немесе мерзімге сезімтал ақпарат үшін МІНДЕТТІ ТҮРДЕ іздеу құралын қолданыңыз
- Ешқашан адамның сезімдерін жеңілдетпеңіз немесе жоққа шығармаңыз
- Дағдарыс жағдайларында кәсіби көмекті ұсыныңыз және дағдарыс телефондарын (іздеу арқылы тауып) беріңіз
- Жылы, қысқа және нақты болыңыз — пайдаланушыны ақпаратпен шамадан тыс жүктемеңіз
- Егер сурет берілсе, оны ойлана зерттеп, эмоционалды мазмұнын ескеріңіз"""


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
        today = datetime.now().strftime("%A, %B %d, %Y")
        prompt = SYSTEM_PROMPT.format(today=today)
        messages = [SystemMessage(content=prompt)] + state["messages"]
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
