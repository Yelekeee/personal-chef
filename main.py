import sys
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agent.graph import build_graph
from src.utils.multimodal import create_image_url_message, create_image_file_message

load_dotenv()

HELP_TEXT = """
Yelnar's Assistant — Commands
───────────────────────────────────────
  <question>      Ask any research question (web search included)
  /image-url      Attach an image via URL and ask about it
  /image-file     Attach a local image file and ask about it
  /new            Start a fresh conversation (clears memory)
  /help           Show this help message
  /quit           Exit the assistant
"""


def get_last_ai_content(result: dict) -> str:
    """Extract the final AI response text from a graph invocation result."""
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.__class__.__name__ == "AIMessage":
            content = msg.content
            if isinstance(content, list):
                parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                return "\n".join(parts)
            return str(content)
    return "(no response)"


def run_query(graph, message: HumanMessage, thread_id: str) -> str:
    """Send a message to the graph and return the assistant's response."""
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [message]}, config=config)
    return get_last_ai_content(result)


def main():
    print("Yelnar's Assistant")
    print("Type /help for available commands.\n")

    graph = build_graph()
    thread_id = str(uuid.uuid4())

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)

        if not user_input:
            continue

        if user_input == "/quit":
            print("Goodbye!")
            sys.exit(0)

        elif user_input == "/help":
            print(HELP_TEXT)

        elif user_input == "/new":
            thread_id = str(uuid.uuid4())
            print("Started a new conversation. Previous context cleared.\n")

        elif user_input == "/image-url":
            image_url = input("Image URL: ").strip()
            if not image_url:
                print("No URL provided.\n")
                continue
            question = input("Your question about the image: ").strip()
            if not question:
                question = "Please describe this image."
            msg = create_image_url_message(question, image_url)
            print("\nAssistant: ", end="", flush=True)
            response = run_query(graph, msg, thread_id)
            print(response, "\n")

        elif user_input == "/image-file":
            image_path = input("Image file path: ").strip()
            if not image_path:
                print("No path provided.\n")
                continue
            question = input("Your question about the image: ").strip()
            if not question:
                question = "Please describe this image."
            try:
                msg = create_image_file_message(question, image_path)
            except FileNotFoundError:
                print(f"File not found: {image_path}\n")
                continue
            print("\nAssistant: ", end="", flush=True)
            response = run_query(graph, msg, thread_id)
            print(response, "\n")

        else:
            msg = HumanMessage(content=user_input)
            print("\nAssistant: ", end="", flush=True)
            response = run_query(graph, msg, thread_id)
            print(response, "\n")


if __name__ == "__main__":
    main()
