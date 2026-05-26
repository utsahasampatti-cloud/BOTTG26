from openai import AsyncOpenAI
from config import OPENAI_API_KEY

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """
    Ліниво створюємо OpenAI client.
    Викликається ТІЛЬКИ коли реально потрібен AI.
    """
    global _client

    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set (runtime)")
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    return _client


async def summarize_from_url(text: str) -> str:
    client = get_client()

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize real estate ad shortly."},
            {"role": "user", "content": text},
        ],
        max_tokens=80,
    )

    return resp.choices[0].message.content.strip()
