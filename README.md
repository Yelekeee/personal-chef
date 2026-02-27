# Personal Research Assistant

A CLI-based AI research assistant that demonstrates all four Module 1 LangGraph concepts.

## Module 1 Concepts Map

| Concept | File | Key API |
|---|---|---|
| **Foundational Models** | `src/agent/graph.py` | `ChatOpenAI`, `SystemMessage`, `.invoke()` |
| **Tools** | `src/tools/search.py` + `graph.py` | `TavilySearchResults`, `.bind_tools()`, `ToolNode` |
| **Short-term Memory** | `src/agent/state.py` + `graph.py` | `add_messages`, `MemorySaver`, `thread_id` |
| **Multimodal** | `src/utils/multimodal.py` | `HumanMessage(content=[{type:text},{type:image_url}])` |

## Project Structure

```
personal_chef/
├── src/
│   ├── agent/
│   │   ├── state.py        # ResearchState TypedDict  ← Memory concept
│   │   └── graph.py        # ReAct graph              ← All 4 concepts
│   ├── tools/
│   │   └── search.py       # Tavily tool              ← Tools concept
│   └── utils/
│       └── multimodal.py   # Image message builders   ← Multimodal concept
├── main.py                  # CLI entry point
├── .env.example             # API key template
└── pyproject.toml
```

## Setup

```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Fill in your API keys in .env
#    OPENAI_API_KEY  — from https://platform.openai.com
#    TAVILY_API_KEY  — from https://tavily.com

# 3. Install dependencies (adds langgraph and syncs lock file)
uv add langgraph
```

## Usage

```bash
python main.py
```

### Commands

| Command | Description |
|---|---|
| `<question>` | Ask any research question — agent searches the web if needed |
| `/image-url` | Attach a remote image by URL and ask a question about it |
| `/image-file` | Attach a local image file and ask a question about it |
| `/new` | Start a fresh conversation (clears short-term memory) |
| `/help` | Show help text |
| `/quit` | Exit |

### Example Session

```
You: What are the latest developments in fusion energy?