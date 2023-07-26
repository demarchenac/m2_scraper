import asyncio
from typing import TypedDict, Literal
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page


class PropertyResult(TypedDict):
    """Typings for results of this scrape process.

    Args:
        TypedDict: Type description lol.
    """

    building: Literal["oficina", "local", "bodega"]
    modality: Literal["ninguna", "arriendo", "venta"]
    neighborhood: str
    city: str
    price: str
    area: str
    bathrooms: str


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

    await page.get_by_placeholder("Ciudad, Zona o Barrio").fill(city)
    await page.locator("id=react-autowhatever-location-section-0-item-0").click()

    await page.get_by_role("button", name="Buscar").click()
    await page.wait_for_url(r"**?search=form")


async def scrape_city_results_pages(page: Page) -> int:
    """Scrapes the number of pages available in the results pagination

    Args:
        page (Page): The current page instance

    Returns:
        int: number of pages
    """

    page_list = await page.locator(".paginator.pagination").get_by_role("listitem").all()
    pages = await page_list[-3].inner_text()
    return int(pages)


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


async def scrape_city_results(page: Page) -> list[PropertyResult]:
    """Generates the property results for the current page on the pagination.

    Args:
        page (Page): The current page instance.

    Returns:
        list[PropertyResult]: This pagination's page as a list of properties.
    """
    items = (
        await page.locator(".realestate-results-list.browse-results-list")
        .get_by_role("navigation")
        .all()
    )

    page: list[PropertyResult] = []

    for item in items:
        texts = await item.all_inner_texts()
        text = texts[0]
        if text.startswith("\t\n\n"):
            pretty = (
                text.replace("\t\n\n", "")
                .replace("\n\nAgregar a favorito\n\t\nContactar", "")
                .replace("\n\n\t", " | ")
                .replace("\n\n", ": ")
                .replace("\n", " | ")
            )

            if "Baños" not in pretty:
                pretty += " | Baños: 0"

            (location, price_tuple, area_tuple, bathrooms_tuple) = tuple(pretty.split(" | "))
            (location_type, neighborhood, city) = tuple(location.split(", "))

            property_type = (
                location_type.replace("en Venta", "")
                .replace("Comercial", "")
                .replace("y Arriendo", "")
                .strip()
                .lower()
            )

            modality = "ninguna"
            if "Arriendo" in location_type:
                modality = "arriendo"
            elif "Venta" in location_type:
                modality = "venta"

            property_result: PropertyResult = {
                "type": property_type,
                "modality": modality,
                "neighborhood": neighborhood.lower(),
                "city": city.lower(),
                "price": price_tuple.split(": ")[1].replace("$", ""),  # goes in COP
                "area": area_tuple.split(": ")[1].replace(" m²", ""),  # goes in m²
                "bathrooms": bathrooms_tuple.split(": ")[1],
            }

            page.append(property_result)
    return page


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
    (playwright, browser, context, page) = await init_playwright(is_headless=False)

    cities = ["Barranquilla", "Soledad", "Puerto Colombia", "Galapa"]
    first_city = cities[0]
    rows: list[PropertyResult] = []

    print(f"Start scrapper @ {url}")

    for city in cities:
        city_rows: list[PropertyResult] = []

        await page.goto(url)
        await goto_city_results(city=city, page=page, only_fill_city=(city != first_city))
        pages = await scrape_city_results_pages(page=page)

        for active_page in range(1, pages + 1):
            await goto_page(page=page, pagination_page=active_page)
            page_results = await scrape_city_results(page=page)
            city_rows.extend(page_results)
        print(f"\t{city}, Results: {len(city_rows)}")

        rows.extend(city_rows)

    print(f"Results from @ {url}: {len(rows)}")

    await close_playwright(playwright=playwright, browser=browser, context=context)


if __name__ == "__main__":
    asyncio.run(main())
