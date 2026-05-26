import asyncio
import random
import json
from io import BytesIO
from pathlib import Path
import ssl
import certifi
import uuid

import requests
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter
from playwright.async_api import async_playwright

# =========================================================
# FAST PATH — JSON-LD
# =========================================================


def extract_photos_json_ld(ad_url: str) -> list[str]:
    r = requests.get(
        ad_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except Exception:
            continue

        if isinstance(data, dict) and "image" in data:
            images = data["image"]
            if isinstance(images, list):
                return [i for i in images if "olxcdn" in i]

    return []


# =========================================================
# FALLBACK — PLAYWRIGHT
# =========================================================


async def extract_photos_playwright(ad_url: str) -> list[str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})

        # блокуємо важке, але НЕ stylesheet
        await context.route(
            "**/*",
            lambda r: (
                r.abort()
                if r.request.resource_type in {"media", "font"}
                else r.continue_()
            ),
        )

        page = await context.new_page()
        await page.goto(ad_url, wait_until="domcontentloaded", timeout=20000)

        photos = await page.evaluate("""
        () => {
            const imgs = Array.from(
              document.querySelectorAll('div[data-testid="ad-photo"] img')
            );

            return imgs
              .map(img =>
                img.src ||
                img.dataset.src ||
                img.dataset.zoomSrc ||
                img.getAttribute("srcset")?.split(" ")[0]
              )
              .filter(Boolean)
              .filter(src => src.includes("olxcdn"));
        }
        """)

        await browser.close()
        return photos


# =========================================================
# PARALLEL DOWNLOAD (RAM)
# =========================================================


async def _download_one(session, url: str) -> Image.Image:
    async with session.get(url, timeout=10) as resp:
        data = await resp.read()
        return Image.open(BytesIO(data)).convert("RGB")


async def download_images_parallel(urls: list[str]) -> list[Image.Image]:
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_download_one(session, u) for u in urls]
        return await asyncio.gather(*tasks)


# =========================================================
# IMAGE HELPERS
# =========================================================


def crop_to_ratio(img: Image.Image, target_ratio: float) -> Image.Image:
    w, h = img.size
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


# =========================================================
# IMAGE MERGE
# =========================================================


def merge_images(
    images: list[Image.Image], height=520, gap=10, ratio=9 / 16
) -> Image.Image:

    prepared = []

    for img in images:
        img = crop_to_ratio(img, ratio)

        scale = height / img.height
        new_width = int(img.width * scale)

        prepared.append(img.resize((new_width, height), Image.LANCZOS))

    total_width = sum(img.width for img in prepared) + gap * (len(prepared) - 1)

    background = (245, 245, 245)
    canvas = Image.new("RGB", (total_width, height), background)

    x = 0
    for img in prepared:
        canvas.paste(img, (x, 0))
        x += img.width + gap

    return canvas


# =========================================================
# WATERMARK
# =========================================================


def add_logo_watermark(
    base: Image.Image,
    logo_path: str = "images/watermark.png",
    scale: float = 0.14,
    margin: int = 20,
    shadow_offset: int = 4,
    shadow_blur: int = 6,
    shadow_opacity: int = 120,
) -> Image.Image:

    if not Path(logo_path).is_file():
        return base.convert("RGB") if base.mode != "RGB" else base

    base = base.convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    target_width = int(base.width * scale)
    ratio = target_width / logo.width
    logo = logo.resize((target_width, int(logo.height * ratio)), Image.LANCZOS)

    x = base.width - logo.width - margin
    y = base.height - logo.height - margin

    # shadow
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, shadow_opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(shadow, (x + shadow_offset, y + shadow_offset), shadow)
    layer.paste(logo, (x, y), logo)

    combined = Image.alpha_composite(base, layer)
    return combined.convert("RGB")


# =========================================================
# MAIN PIPELINE
# =========================================================


async def build_composite(ad_url: str, output_dir="output") -> str:
    photos = extract_photos_json_ld(ad_url)

    if len(photos) < 3:
        print("⚠️ JSON-LD не дав достатньо фото — fallback Playwright")
        photos = await extract_photos_playwright(ad_url)

    if len(photos) < 1:
        raise RuntimeError("Фото не знайдені взагалі")

    selected = random.sample(photos, min(3, len(photos)))
    images = await download_images_parallel(selected)

    result = merge_images(images)
    result = add_logo_watermark(result)

    Path(output_dir).mkdir(exist_ok=True)
    out_path = Path(output_dir) / f"preview_{uuid.uuid4().hex}.jpg"

    result.save(
        out_path,
        "JPEG",
        quality=85,
        optimize=True,
        progressive=True,
    )

    return str(out_path)


# =========================================================
# ENTRYPOINT (local test)
# =========================================================


async def main():
    print("🔗 Встав URL оголошення OLX:")
    url = input().strip()

    if not url.startswith("http"):
        url = "https://" + url

    out = await build_composite(url)
    print(f"\n✅ Готово: {out}")


if __name__ == "__main__":
    asyncio.run(main())
