import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.api.emotion_models import EmotionResult
from src.utils.multimodal import create_image_file_message

_EMOTION_SCHEMA = """{
  "emotion": "<happy|neutral|stressed|sad|anxious>",
  "level": "<low|medium|high>",
  "confidence": <float 0.0-1.0>,
  "analysis": "<1-2 сөйлемдік түсіндірме қазақ тілінде>",
  "recommendations": ["<1-элемент қазақша>", "<2-элемент қазақша>", "<3-элемент қазақша>"],
  "mental_health_note": "<қазақша жол немесе null>"
}"""

_SYSTEM_BASE = """Сіз эмоцияны талдайтын AI жүйесісіз. Берілген мәліметті талдап, тек қана осы схемаға сәйкес жарамды JSON қайтарыңыз:

{schema}

Ережелер:
- emotion: дәл осы мәндердің бірін таңдаңыз: happy, neutral, stressed, sad, anxious (ағылшынша, өзгертпеңіз)
- level: қарқындылықты low, medium немесе high деп белгілеңіз (ағылшынша, өзгертпеңіз)
- confidence: 0.0-ден 1.0-ге дейінгі сенімділік коэффициенті
- analysis: ҚАЗАҚ тілінде 1-2 сөйлем, эмоционалды жағдайды түсіндіреді
- recommendations: ҚАЗАҚ тілінде 3-5 іс-шара, эмоцияға байланысты:
  * stressed немесе anxious → бірінші ұсыным міндетті түрде 4-7-8 тыныс алу техникасы болуы керек (4 секунд дем алу, 7 секунд ұстап тұру, 8 секунд дем шығару) — қазақша сипаттама
  * sad → музыкалық жанр ұсынысы және жеңіл дене белсенділігі — қазақша
  * happy → оң жағдайды нығайтатын және бөлісетін іс-шаралар — қазақша
  * neutral → зейін және зерттеу іс-шаралары — қазақша
- mental_health_note: тек emotion "stressed" немесе "anxious" ЖӘНЕ level "high" болса ғана қолдаушы жазба жазыңыз (ҚАЗАҚША); басқа жағдайда null қойыңыз

ТЕК JSON объектісін қайтарыңыз, markdown бөлгіштерсіз, қосымша мәтінсіз."""

_FACE_SYSTEM = _SYSTEM_BASE.format(schema=_EMOTION_SCHEMA) + "\n\nБерілген суреттегі бет-әлпетті талдаңыз."
_TEXT_SYSTEM = _SYSTEM_BASE.format(schema=_EMOTION_SCHEMA) + "\n\nБерілген мәтіннің эмоционалды мазмұнын талдаңыз."


def _parse_result(raw: str) -> EmotionResult:
    """Parse LLM string response into EmotionResult, stripping markdown fences defensively."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop first and last fence lines
        inner = lines[1:-1] if lines[-1].strip().startswith("```") else lines[1:]
        text = "\n".join(inner).strip()
    data = json.loads(text)
    return EmotionResult(**data)


async def analyze_face(image_path: str) -> EmotionResult:
    """Analyze facial emotion from a local image file."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Build multimodal message using existing utility
    human_msg = create_image_file_message(
        "Осы суреттегі бет-әлпетті талдап, эмоция JSON мәнін қайтарыңыз.",
        image_path,
    )

    response = await llm.ainvoke([
        SystemMessage(content=_FACE_SYSTEM),
        human_msg,
    ])

    return _parse_result(response.content)


async def analyze_text(text: str) -> EmotionResult:
    """Analyze emotion from a text passage."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    response = await llm.ainvoke([
        SystemMessage(content=_TEXT_SYSTEM),
        HumanMessage(content=text),
    ])

    return _parse_result(response.content)
