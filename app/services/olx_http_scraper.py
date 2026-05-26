import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import asyncio


BASE_DOMAIN = "https://www.olx.pl"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "pl-PL,pl;q=0.9",
}


# ==============================
# URL PAGINATION
# ==============================
def build_page_url(base_url: str, page_num: int) -> str:
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["page"] = [str(page_num)]
    return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))


# ==============================
# FETCH
# ==============================
async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url)
    r.raise_for_status()
    return r.text


# ==============================
# PARSE
# ==============================
def parse_ads(html: str) -> list[dict]:
    tree = HTMLParser(html)
    ads = []

    cards = tree.css('div[data-cy="l-card"]')

    for card in cards:
        link = card.css_first("a")
        if not link:
            continue

        href = link.attributes.get("href")
        if not href:
            continue

        full_url = urljoin(BASE_DOMAIN, href)

        price_el = card.css_first('[data-testid="ad-price"]')
        price = price_el.text(strip=True) if price_el else None
         
        if  "olx.pl" not in full_url:
            continue 
        ads.append({
            "url": full_url,
            "price": price,
        })

    return ads


# ==============================
# MAIN SEARCH
# ==============================
async def search_olx_http(
    base_url: str,
    max_pages: int = 2,
    max_ads: int = 25,
) -> list[dict]:

    ads: list[dict] = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=15,
        follow_redirects=True,
    ) as client:

        for page_num in range(1, max_pages + 1):
            page_url = build_page_url(base_url, page_num)

            html = await fetch_page(client, page_url)
            page_ads = parse_ads(html)

            for ad in page_ads:
                ads.append(ad)

                if len(ads) >= max_ads:
                    return ads

            # anti-bot safety pause
            await asyncio.sleep(1)

    return ads
