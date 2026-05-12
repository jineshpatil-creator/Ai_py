import pytest
import allure
from pages.home_page import HomePage
from utils.logger import log

@allure.feature("UI Visual Testing")
@allure.story("Homepage AI Validation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
def test_homepage_visual_with_ai(page, ai):
    """
    Test the homepage visually using Gemini AI.
    This test uses the Page Object Model (HomePage) and the AI Validator.
    """
    with allure.step("Initialize Page Object and navigate to homepage"):
        home_page = HomePage(page)
        home_page.navigate("https://example.com")

    with allure.step("Capture full-page screenshot"):
        screenshot_path = home_page.take_full_page_screenshot()
        log.info(f"Screenshot saved to {screenshot_path}")
        allure.attach.file(screenshot_path, name="Homepage Screenshot", attachment_type=allure.attachment_type.PNG)

    with allure.step("Analyze screenshot with Gemini AI"):
        prompt = """
        Act as an expert QA automation engineer. Analyze the provided screenshot of the website.
        1. Verify if the page loaded correctly without obvious visual errors.
        2. Check if there is a main heading (H1) visible on the page.
        
        Respond in the following format exactly:
        RESULT: [PASS or FAIL]
        REASON: [Your detailed explanation]
        """
        ai_response = ai.analyze_screenshot(screenshot_path, prompt)
        log.info(f"--- AI Analysis Result ---\n{ai_response}\n--------------------------")
        allure.attach(ai_response, name="AI Analysis", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Assert AI validation result is PASS"):
        assert "RESULT: PASS" in ai_response, f"AI Visual Test Failed! Reason: {ai_response}"
