from playwright.async_api import async_playwright

from services.fast_links_D import collect_links_fast


async def run_fast_links(start_url: str) -> list[dict]:
    """
    Запускає Playwright і збирає оголошення через fast_links_D
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            ads = await collect_links_fast(page, start_url)
            return ads
        finally:
            await browser.close()
