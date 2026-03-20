"""Export the challenge flyer to PDF and PNG using headless Chromium."""

import asyncio
import logging
from pathlib import Path

from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

FLYER_HTML = Path(__file__).parent / "index.html"
OUT_PDF = Path(__file__).parent / "TechQuest_Prompt_Challenge_Flyer.pdf"
OUT_PNG = Path(__file__).parent / "TechQuest_Prompt_Challenge_Flyer.png"


async def export() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 816, "height": 1200})

        await page.goto(FLYER_HTML.as_uri())
        # Wait for fonts and layout to settle
        await page.wait_for_load_state("networkidle")

        # Measure actual flyer height and compute exact scale to fill Letter
        flyer_height: float = await page.eval_on_selector(
            ".flyer", "el => el.getBoundingClientRect().height"
        )
        page_height_px = 1056.0  # 11in at 96dpi
        scale = round(min(page_height_px / flyer_height, 2.0), 4)
        logger.info("Flyer height: %.1fpx  →  scale: %.4f", flyer_height, scale)

        # ── PDF ──────────────────────────────────────────────────────────────
        await page.pdf(
            path=str(OUT_PDF),
            print_background=True,
            width="8.5in",
            height="11in",
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            prefer_css_page_size=False,
            scale=scale,
        )
        logger.info("✅ PDF saved  → %s", OUT_PDF.name)

        # ── PNG ──────────────────────────────────────────────────────────────
        flyer = page.locator(".flyer")
        await flyer.screenshot(path=str(OUT_PNG), type="png")
        logger.info("✅ PNG saved  → %s", OUT_PNG.name)

        await browser.close()


def run() -> None:
    asyncio.run(export())


if __name__ == "__main__":
    run()
