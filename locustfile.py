from locust import HttpUser, task


class So1sUser(HttpUser):
    @task
    def hello_world(self):
        self.client.post("/livez")
