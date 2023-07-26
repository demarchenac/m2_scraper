from playwright.async_api import Page

# pylint: disable-next=import-error
from utils.hints.property_result import PropertyResult


async def get_pages_of_city_results(page: Page) -> int:
    """Scrapes the number of pages available in the results pagination

    Args:
        page (Page): The current page instance

    Returns:
        int: number of pages
    """

    page_list = await page.locator(".paginator.pagination").get_by_role("listitem").all()
    pages = await page_list[-3].inner_text()
    return int(pages)


async def get_city_results_of_current_page(page: Page) -> list[PropertyResult]:
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
                # goes in COP
                "price": price_tuple.split(": ")[1].replace("$", "").replace(".", ""),
                # goes in m²
                "area": area_tuple.split(": ")[1].replace(" m²", ""),
                "bathrooms": bathrooms_tuple.split(": ")[1],
            }

            page.append(property_result)
    return page
