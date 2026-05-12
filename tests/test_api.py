import pytest
import allure
from api.api_client import APIClient

@pytest.fixture
def api_client(playwright):
    """Fixture to set up the Playwright APIRequestContext."""
    request_context = playwright.request.new_context()
    yield APIClient(request_context)
    request_context.dispose()

@allure.feature("API Testing")
@allure.story("GET All Posts")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
def test_get_all_posts(api_client):
    """Verify that a GET request returns a 200 status code and data."""
    with allure.step("Send GET request to /posts"):
        response = api_client.get_posts()

    with allure.step("Verify status code is 200"):
        assert response["status"] == 200, f"Expected 200, got {response['status']}"

    with allure.step("Verify response contains posts with 'id' field"):
        assert len(response["body"]) > 0, "Expected a list of posts, got an empty list"
        assert "id" in response["body"][0], "Expected 'id' field in the post data"

@allure.feature("API Testing")
@allure.story("POST Create New Resource")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
def test_create_new_post(api_client):
    """Verify that a POST request successfully creates a resource."""
    payload = {
        "title": "QA Automation Rest Test",
        "body": "This is a test created via Playwright API testing.",
        "userId": 1
    }

    with allure.step(f"Send POST request with payload: {payload['title']}"):
        response = api_client.create_post(payload)

    with allure.step("Verify status code is 201 Created"):
        assert response["status"] == 201, f"Expected 201, got {response['status']}"

    with allure.step("Verify response title matches payload"):
        assert response["body"]["title"] == payload["title"], "Response title did not match payload"
