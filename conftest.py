import pytest
import allure
from utils.ai_validator import AIValidator


@pytest.fixture(scope="session")
def ai():
    """Returns an instance of the AI Validator to use in tests."""
    return AIValidator()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Auto-attach a screenshot to Allure when a UI test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Check if the test has a 'page' fixture (i.e., it's a browser test)
        page = item.funcargs.get("page", None)
        if page:
            try:
                screenshot_bytes = page.screenshot(full_page=True)
                allure.attach(
                    screenshot_bytes,
                    name="Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass  # Page may already be closed
