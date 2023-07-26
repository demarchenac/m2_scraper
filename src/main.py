import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page


async def init_playwright(
    url: str, is_headless: bool
) -> tuple[Playwright, Browser, BrowserContext, Page]:
    """Generates a PlayWright instance

    Args:
        url (str): url to scrape, expected to be "https://metrocuadrado.com".
        is_headless (bool): flag to open the browser headless or not.

    Returns:
        tuple[Playwright, Browser, BrowserContext, Page]: _description_
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=is_headless)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url)
    await context.close()
    await browser.close()
    await playwright.stop()

    return (playwright, browser, context, page)


async def goto_city_results(city: str, page: Page):
    """Navigates to metrocuadrado results for a given city

    Args:
        city (str): The city results to browse
        page (Page): Page instance
    """
    # page


pass


async def close_playwright(playwright: Playwright, browser: Browser, context: BrowserContext):
    """Closes the PlayWright instance

    Args:
        playwright (Playwright): PlayWright context manager
        browser (Browser): Playwright browser instance
        context (BrowserContext): Browser context (cookies, cache, etc)
    """
    await context.close()
    await browser.close()
    await playwright.stop()


async def main():
    """Runs the PlayWright web scrapper for https://metrocuadrado.com"""

    url = "https://www.metrocuadrado.com/"
    (playwright, browser, context, page) = await init_playwright(url=url, is_headless=False)

    cities = ["Barranquilla", "Soledad", "Puerto Colombia", "Galapa"]

    for city in cities:
        await goto_city_results(city=city, page=page)

    await close_playwright(playwright=playwright, browser=browser, context=context)


if __name__ == "__main__":
    asyncio.run(main())
