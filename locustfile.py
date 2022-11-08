from locust import FastHttpUser, task
import uuid
import time


class So1sUser(FastHttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.model_metadata = None

    @task
    def main_task(self):
        self.login()
        self.create_model()
        self.create_deployment()
        self.load_test_endpoint()
        self.delete_deployment()
        self.delete_model()

    def login(self):
        self.client.post(
            "/api/v1/signin", {"username": "so1s", "password": "admin12345"})

    def create_model(self):
        self.model_name = str(uuid.uuid4())

        post_response = self.client.post(
            "/api/v1/models", {"name": self.model_name,
                               'library': 'keras',
                               'inputShape': '(1,)',
                               'inputDType': 'numpy',
                               'outputShape': '(1,)',
                               'inputDType': 'numpy',
                               'deviceType': 'CPU'})

        time.sleep(1)

        models = self.client.get("/api/v1/models").json()
        self.model = [e for e in models if e["name"]
                      == post_response["modelName"]][0]

        self.model_metadata = self.client.get(
            f"/api/v1/models/${self.model['id']}").json()[0]

    def delete_model(self):
        self.client.delete(
            f"/api/v1/models/${self.model['id']}/versions/{self.model_metadata['version']}")

        time.sleep(1)

        self.client.delete(
            f"/api/v1/models/${self.model['id']}")

    def create_deployment(self):
        pass

    def delete_deployment(self):
        pass

    def load_test_endpoint(self):
        pass
