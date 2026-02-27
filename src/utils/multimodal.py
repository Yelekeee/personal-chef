import base64
from pathlib import Path
from langchain_core.messages import HumanMessage


def create_image_url_message(text: str, image_url: str) -> HumanMessage:
    """Build a multimodal HumanMessage from a remote image URL."""
    return HumanMessage(
        content=[
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
    )


def create_image_file_message(text: str, image_path: str) -> HumanMessage:
    """Build a multimodal HumanMessage from a local image file (base64-encoded)."""
    path = Path(image_path)
    suffix = path.suffix.lower().lstrip(".")
    mime_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}
    mime_type = mime_map.get(suffix, "jpeg")

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    data_url = f"data:image/{mime_type};base64,{encoded}"
    return HumanMessage(
        content=[
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]
    )
