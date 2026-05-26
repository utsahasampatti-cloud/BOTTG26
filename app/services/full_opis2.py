import asyncio
from services.ai_olx import summarize_from_url


async def build_short_opis_from_url(ad_url: str) -> str | None:
    """
    Приймає URL оголошення.
    Повертає 1 коротке речення українською,
    згенероване ТІЛЬКИ на базі URL.
    """

    if not ad_url or len(ad_url) < 10:
        return None

    try:
        return await asyncio.wait_for(
            summarize_from_url(ad_url),
            timeout=2.5,  # ⚡ дуже швидко
        )
    except Exception:
        return None
