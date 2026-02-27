from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    # add_messages reducer APPENDS new messages instead of overwriting
    # This is what gives the agent memory across turns within a thread
    messages: Annotated[list[BaseMessage], add_messages]
