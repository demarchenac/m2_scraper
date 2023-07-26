from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page


async def init_playwright(
    is_headless: bool = False,
) -> tuple[Playwright, Browser, BrowserContext, Page]:
    """Generates a PlayWright instance

    Args:
        url (str): url to scrape, expected to be "https://metrocuadrado.com".
        is_headless (bool): flag to open the browser headless or not.

    Returns:
        tuple[Playwright, Browser, BrowserContext, Page]: navigation specs.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=is_headless)
    context = await browser.new_context()
    page = await context.new_page()

    return (playwright, browser, context, page)


async def goto_city_results(city: str, page: Page, only_fill_city=False):
    """Navigates to metrocuadrado results for a given city

    Args:
        city (str): The city results to browse
        page (Page): Page instance
        only_fill_city (bool, optional): Are we searching the first city?
    """
    if not only_fill_city:
        await page.locator("id=propertyTypes").click()
        await page.locator("id=react-select-2-option-2", has_text="Oficinas").click()
        await page.locator("id=react-select-2-option-3", has_text="Locales").click()
        await page.locator("id=react-select-2-option-4", has_text="Bodegas").click()
        await page.locator("id=propertyTypes").click()

        await page.locator("id=businessType").click()
        await page.locator("id=react-select-3-option-2", has_text="Compra Nuevo y Usado").click()
        await page.locator("id=businessType").click()

    if only_fill_city:
        await page.get_by_placeholder("Ciudad, Zona o Barrio").clear()
        await page.wait_for_timeout(1000)

    await page.get_by_placeholder("Ciudad, Zona o Barrio").fill(city)
    await page.wait_for_timeout(2000)
    await page.locator("id=react-autowhatever-location-section-0-item-0").click()

    await page.get_by_role("button", name="Buscar").click()
    await page.wait_for_url(r"**?search=form")


async def goto_page(page: Page, pagination_page: int):
    """Navigates to an specific pagination page

    Args:
        page (Page): The current page instance
        pagination_page (int): The desired pagination to navigate
    """
    page_to_navigate = page.get_by_role("link", name=str(pagination_page), exact=True)
    await page_to_navigate.scroll_into_view_if_needed()
    await page_to_navigate.click(force=True)
    await page.wait_for_url(r"**?search=form")
    await page.wait_for_timeout(1000)


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
