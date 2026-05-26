from playwright.async_api import Page
from urllib.parse import (
    urljoin,
    urlparse,
    parse_qs,
    urlencode,
    urlunparse,
)
import re

# =======================
# DEBUG CONFIG
# =======================
DEBUG_FAST = True


def debug(msg: str):
    if DEBUG_FAST:
        print(f"[FAST_DEBUG] {msg}", flush=True)


debug("fast_links_D.py loaded")


# =======================
# URL BUILDER
# =======================
def build_page_url(base_url: str, page_num: int) -> str:
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["page"] = [str(page_num)]
    return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))


# =======================
# COOKIE KILLER
# =======================
async def _kill_cookies(page: Page):
    debug("Killing cookie banners")
    await page.evaluate("""
        () => {
            document.querySelectorAll(
                '[id*="onetrust"], [class*="onetrust"]'
            ).forEach(e => e.remove());
            document.body.style.overflow = 'auto';
        }
    """)


# =======================
# MAIN COLLECTOR
# =======================
async def collect_links_fast(page: Page, start_url: str) -> list[dict]:
    debug(f"START collect_links_fast | url={start_url}")

    ads: list[dict] = []
    seen_ids: set[str] = set()
    page_num = 1

    while True:
        page_url = build_page_url(start_url, page_num)
        debug(f"OPEN PAGE {page_num}: {page_url}")

        await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
        await _kill_cookies(page)

        try:
            await page.wait_for_selector('div[data-cy="l-card"]', timeout=30000)
        except Exception:
            debug("NO cards selector found — STOP")
            return ads

        cards = await page.query_selector_all('div[data-cy="l-card"]')
        debug(f"CARDS FOUND: {len(cards)}")

        if not cards:
            debug("EMPTY page — STOP")
            return ads

        # 🔥 КРИТИЧНО: йдемо по картках ПО ЧЕРЗІ
        for idx, c in enumerate(cards, start=1):
            debug(f"-- CARD {idx}")

            ad_id = await c.get_attribute("id")
            debug(f"   ad_id={ad_id}")

            if not ad_id or ad_id in seen_ids:
                debug("   SKIP: no id or duplicate")
                continue

            # -----------------------
            # AREA — КРИТИЧНА УМОВА
            # -----------------------
            full_text = (await c.inner_text()).strip()
            match = re.search(r"(\d+(?:[.,]\d+)?)\s*m²", full_text)

            if not match:
                debug(f"🛑 STOP: card #{idx} WITHOUT m² — terminate whole search")
                return ads  # ❗ МИТТЄВИЙ СТОП УСЬОГО СКРИПТА

            area = match.group(1) + " m²"
            debug(f"   area={area}")

            # -----------------------
            # LINK
            # -----------------------
            link_el = await c.query_selector("a[href]")
            if not link_el:
                debug("   SKIP: no link")
                continue

            href = await link_el.get_attribute("href")
            if not href:
                debug("   SKIP: empty href")
                continue

            full_url = urljoin(page.url, href)
            parsed = urlparse(full_url)

            if parsed.netloc != "www.olx.pl":
                debug(f"   SKIP: external domain {parsed.netloc}")
                continue

            # -----------------------
            # PRICE
            # -----------------------
            price = None
            price_el = await c.query_selector('p[data-testid="ad-price"]')
            if price_el:
                price = (await price_el.inner_text()).strip()

            debug(f"   price={price}")

            # -----------------------
            # SAVE AD
            # -----------------------
            ads.append(
                {
                    "id": ad_id,
                    "url": full_url,
                    "price": price,
                    "area_m2": area,
                }
            )
            seen_ids.add(ad_id)

            debug("   AD ADDED")

        # ▶️ якщо ДОСЮДИ дійшли — всі картки мали m²
        next_btn = await page.query_selector('a[data-testid="pagination-forward"]')
        debug(f"NEXT BUTTON EXISTS: {bool(next_btn)}")

        if not next_btn:
            debug("NO next page — STOP")
            return ads

        page_num += 1

    # формально сюди не дійдемо
    return ads
