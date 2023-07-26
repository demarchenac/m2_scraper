import asyncio
from playwright.async_api import async_playwright

async def main():
  """Runs the PlayWright web scrapper for https://metrocuadrado.com"""

  playwright = await async_playwright().start()
  browser = await playwright.chromium.launch(headless=False)
  context = await browser.new_context()
  page = await context.new_page()
  await page.goto("https://www.metrocuadrado.com/")
  await context.close()
  await browser.close()
  await playwright.stop()


if __name__ == "__main__":
  asyncio.run(main())
