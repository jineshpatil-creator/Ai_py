import allure
from pytest_bdd import scenario, given, when, then, parsers
from pages.home_page import HomePage
from utils.data_reader import load_test_data
from utils.logger import log
import pytest

# Link this test to the feature file
@allure.feature("BDD Visual Testing")
@allure.story("Data-Driven AI Validation")
@allure.severity(allure.severity_level.CRITICAL)
@scenario('homepage.feature', 'Visual AI Validation across multiple websites')
def test_homepage_ai_validation():
    pass

@pytest.fixture
def shared_data():
    """A dictionary to store data between steps."""
    return {}

@given('I load the test data')
def load_data(shared_data):
    with allure.step("Load JSON test data from data/test_data.json"):
        shared_data['test_cases'] = load_test_data()
        log.info("Loaded JSON test data successfully.")

@when(parsers.parse('I navigate to the {url}'))
def navigate_to_url(page, url):
    with allure.step(f"Navigate to {url}"):
        home_page = HomePage(page)
        home_page.navigate(url)
        log.info(f"Navigated to {url}")

@when('I take a full-page screenshot')
def take_screenshot(page, shared_data):
    with allure.step("Capture full-page screenshot"):
        home_page = HomePage(page)
        import time
        filename = f"screenshot_{int(time.time())}.png"
        screenshot_path = home_page.take_full_page_screenshot(filename)
        shared_data['screenshot_path'] = screenshot_path
        log.info(f"Screenshot saved to {screenshot_path}")
        allure.attach.file(screenshot_path, name="Page Screenshot", attachment_type=allure.attachment_type.PNG)

@then(parsers.parse('the AI validator should confirm the page looks correct and has heading {expected_heading}'))
def validate_with_ai(ai, shared_data, expected_heading):
    with allure.step(f"Validate with AI — expecting heading: {expected_heading}"):
        screenshot_path = shared_data['screenshot_path']
        prompt = f"""
        Act as an expert QA automation engineer. Analyze the provided screenshot of the website.
        1. Verify if the page loaded correctly without obvious visual errors.
        2. Check if there is a main heading visible on the page that contains the text: "{expected_heading}".
        
        Respond in the following format exactly:
        RESULT: [PASS or FAIL]
        REASON: [Your detailed explanation]
        """
        ai_response = ai.analyze_screenshot(screenshot_path, prompt)
        log.info(f"--- AI Analysis Result ---\n{ai_response}\n--------------------------")
        allure.attach(ai_response, name="AI Analysis Result", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Assert AI result is PASS"):
        assert "RESULT: PASS" in ai_response, f"AI Visual Test Failed! Reason: {ai_response}"
