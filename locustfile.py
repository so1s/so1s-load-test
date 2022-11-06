from locust import FastHttpUser, task


class So1sUser(FastHttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = {}
        self.deployments = []

    def on_start(self):
        self.login()

    def login(self):
        self.client.post(
            "/api/v1/signin", {"username": "so1s", "password": "admin12345"})

    def create_model(self):
        pass

    def delete_model(self):
        pass

    def create_deployments(self):
        pass

    def delete_deployments(self):
        pass

    def load_endpoints(self):
        pass

    @task
    def main_task(self):
        self.client.post("/livez")
