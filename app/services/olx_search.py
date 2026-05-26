from playwright.async_api import async_playwright
from services.fast_links_D import collect_links_fast


async def search_olx_ads(search_url: str) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        ads = await collect_links_fast(page, search_url)

        await browser.close()

    return ads
