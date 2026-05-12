from playwright.sync_api import Page

class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.url = "https://example.com"

    def navigate(self, url: str):
        """Navigates to the provided URL."""
        self.page.goto(url)

    def take_full_page_screenshot(self, filename: str = "homepage_screenshot.png") -> str:
        """Takes a full page screenshot and returns the file path."""
        self.page.screenshot(path=filename, full_page=True)
        return filename
