from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Wait between 1 and 5 seconds before the next task is executed
    wait_time = between(1, 5)
    
    # Base URL is usually passed via the command line (--host)
    # but we can set a default here.
    host = "https://jsonplaceholder.typicode.com"

    @task(3)
    def view_all_posts(self):
        """Simulates a user viewing the main list of posts (higher weight = more frequent)."""
        self.client.get("/posts", name="View All Posts")

    @task(1)
    def view_single_post(self):
        """Simulates a user clicking into a specific post."""
        # Randomly hitting post #1 just as an example
        self.client.get("/posts/1", name="View Single Post")

    @task(1)
    def create_new_post(self):
        """Simulates a user submitting a form to create a new post."""
        payload = {
            "title": "Load Test Title",
            "body": "Load Test Body",
            "userId": 1
        }
        self.client.post("/posts", json=payload, name="Create Post")

    def on_start(self):
        """Called when a Locust user starts before any task is scheduled."""
        print("A new user has started load testing.")
