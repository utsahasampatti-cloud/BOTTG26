from playwright.async_api import Page
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

DEBUG_FAST = True


def debug(msg: str):
    if DEBUG_FAST:
        print(f"[FAST_DEBUG] {msg}")


def build_page_url(base_url: str, page_num: int) -> str:
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["page"] = [str(page_num)]
    return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))

    debug("fast_links.py loaded")
    debug(f"build_page_url exists: {'build_page_url' in globals()}")


async def _kill_cookies(page: Page):
    await page.evaluate("""
        () => {
            document.querySelectorAll(
                '[id*="onetrust"], [class*="onetrust"]'
            ).forEach(e => e.remove());
            document.body.style.overflow = 'auto';
        }
    """)


async def collect_links_fast(page: Page, start_url: str) -> list[dict]:
    ads = []
    seen_ids = set()
    page_num = 1

    while True:
        page_url = build_page_url(start_url, page_num)
        print(f"📄 FAST | сторінка {page_num}")

        await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
        await _kill_cookies(page)

        await page.wait_for_selector('div[data-cy="l-card"]', timeout=30000)
        cards = await page.query_selector_all('div[data-cy="l-card"]')
        print(f"   🔎 знайдено {len(cards)} оголошень")

        for c in cards:
            ad_id = await c.get_attribute("id")
            if not ad_id or ad_id in seen_ids:
                continue

            link_el = await c.query_selector("a[href]")
            if not link_el:
                continue

            href = await link_el.get_attribute("href")
            if not href:
                continue

            full_url = urljoin(page.url, href)

            parsed = urlparse(full_url)
            if parsed.netloc != "https://www.olx.pl/":
                continue

            # 💰 ЦІНА
            price = None
            price_el = await c.query_selector('p[data-testid="ad-price"]')
            if price_el:
                price = (await price_el.inner_text()).strip()

            # 📐 ПЛОЩА
            area = None
            area_el = await c.query_selector(
                'span[data-testid="blueprint-card-param-icon"]'
            )
            if area_el:
                txt = (await area_el.inner_text()).strip()
                if "m²" in txt:
                    area = txt.split("·")[0].strip()

            ads.append({"id": ad_id, "url": full_url, "price": price, "area": area})

            seen_ids.add(ad_id)

        # ▶️ ПАГІНАЦІЯ
        next_btn = await page.query_selector('a[data-testid="pagination-forward"]')
        if not next_btn:
            print("🛑 FAST | кнопки 'Далі' більше нема — стоп")
            break

        page_num += 1

    print(f"✅ FAST | усього зібрано {len(ads)} оголошень")
    return ads
