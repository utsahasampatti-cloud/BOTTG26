import json
import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError

from services.ai_olx import summarize_opis

# =========================================================
# FAST PATH — JSON-LD
# =========================================================


def extract_opis_json_ld(ad_url: str) -> str | None:
    try:
        r = requests.get(
            ad_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except Exception:
            continue

        if isinstance(data, dict):
            desc = data.get("description")
            if isinstance(desc, str) and len(desc.strip()) > 50:
                return desc.strip()

    return None


# =========================================================
# FALLBACK — PLAYWRIGHT
# =========================================================


async def extract_opis_playwright(ad_url: str) -> str | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})

        # блокуємо важке
        await context.route(
            "**/*",
            lambda r: (
                r.abort()
                if r.request.resource_type in {"media", "font"}
                else r.continue_()
            ),
        )

        page = await context.new_page()

        try:
            await page.goto(ad_url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_selector("h3", timeout=8000)

            opis = await page.evaluate("""
                () => {
                    const h = document.evaluate(
                        "//h3[normalize-space()='Opis']",
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;

                    if (!h) return null;

                    for (const d of h.parentElement.querySelectorAll("div")) {
                        const t = d.innerText.trim();
                        if (t.length > 50) return t;
                    }
                    return null;
                }
                """)

            return opis

        except TimeoutError:
            return None

        finally:
            await browser.close()


# =========================================================
# PUBLIC PIPELINE
# =========================================================


async def build_short_opis(ad_url: str) -> str | None:
    """
    Головна функція.
    Повертає короткий опис або None."""

    print("🔥 build_short_opis CALLED", ad_url)

    # 1️⃣ пробуємо швидкий шлях
    opis = extract_opis_json_ld(ad_url)

    # 2️⃣ fallback
    if not opis:
        opis = await extract_opis_playwright(ad_url)

    if not opis:
        return None

    # 3️⃣ AI summary (з таймаутом)
    try:
        return await asyncio.wait_for(
            summarize_opis(opis),
            timeout=12,
        )
    except Exception:
        return None
