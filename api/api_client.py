from playwright.sync_api import APIRequestContext

class APIClient:
    """Helper class to make REST API requests using Playwright."""
    def __init__(self, request_context: APIRequestContext):
        self.request = request_context
        self.base_url = "https://jsonplaceholder.typicode.com"

    def get_posts(self) -> dict:
        """Sends a GET request to retrieve all posts."""
        response = self.request.get(f"{self.base_url}/posts")
        return {
            "status": response.status,
            "body": response.json()
        }

    def create_post(self, payload: dict) -> dict:
        """Sends a POST request to create a new post."""
        response = self.request.post(f"{self.base_url}/posts", data=payload)
        return {
            "status": response.status,
            "body": response.json()
        }
