import asyncio
from utils.pandas import save
from utils.playwright import navigation, scrape

# pylint: disable-next=import-error
from utils.hints.property_result import PropertyResult


async def run_scraper(cities: list[str], url: str, is_headless=False):
    """Runs the scrape process

    Args:
        cities (list[str]): List of cities to scrape within the url.
        url (str): The url to scrape.
        is_headless (bool, optional): flag to open the browser headless or not. Defaults to False.
    """
    rows: list[PropertyResult] = []

    (playwright, browser, context, page) = await navigation.init_playwright(is_headless=is_headless)

    print(f"Start scraper @ {url}")

    for city in cities:
        city_rows: list[PropertyResult] = []

        for result_type in ["sales", "rent"]:
            await page.goto(url)
            await navigation.goto_city_results(
                city=city,
                page=page,
                only_fill_city=(city != cities[0]),
                results_type=result_type,
            )

            pages = await scrape.get_pages_of_city_results(page)

            for active_page in range(1, pages + 1):
                await navigation.goto_page(page=page, pagination_page=active_page)
                page_results = await scrape.get_city_results_of_current_page(page)

                city_rows.extend(page_results)

        print(f"\t{city}, Results: {len(city_rows)}")

        rows.extend(city_rows)

    await navigation.close_playwright(playwright=playwright, browser=browser, context=context)

    print(f"Results from @ {url}: {len(rows)}")

    save.to_csv(rows)


async def main():
    """Runs the PlayWright web scraper for https://metrocuadrado.com"""

    url = "https://www.metrocuadrado.com/"
    cities = ["Barranquilla", "Soledad", "Puerto Colombia", "Galapa"]

    await run_scraper(url=url, cities=cities)


if __name__ == "__main__":
    asyncio.run(main())
