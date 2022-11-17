from locust import FastHttpUser, task
import uuid
import random


def generate_id():
    while True:
        id = str(uuid.uuid4())

        if id[0].isalpha():
            return id.replace('-', '')


class So1sUser(FastHttpUser):
    network_timeout = 300000.0
    connection_timeout = 300000.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = self.get_auth_token()

    def get_auth_token(self):
        res = self.client.post("/api/v1/signin",
                               json={"username": "so1s", "password": "admin12345"})

        return res.json()["token"]

    @property
    def auth_header(self):
        return {"authorization": "Bearer " + self.token}

    @task
    def get_models(self) -> list[dict]:
        return self.client.get(
            "/api/v1/models", headers=self.auth_header).json()

    @task
    def get_resources(self) -> list[dict]:
        return self.client.get("/api/v1/resources", headers=self.auth_header).json()

    @task
    def get_deployments(self) -> list[dict]:
        return self.client.get("/api/v1/deployments", headers=self.auth_header).json()

    def get_model_metadata(self, model: dict):
        return self.client.get(f"/api/v1/models/{model['id']}", headers=self.auth_header).json()

    @task
    def create_model(self):
        model_name = generate_id()

        self.client.post(
            "/api/v1/models", headers=self.auth_header,
            files=[  # https://superuser.com/a/960710/1159180
                ('modelFile', ('model.zip', open('./models/efficientnet.zip', 'rb'), 'application/gzip'))],
            data={"name": model_name,
                  'library': 'keras',
                  'inputShape': '(1,)',
                  'inputDtype': 'numpy',
                  'outputShape': '(1,)',
                  'outputDtype': 'numpy',
                  'deviceType': 'CPU'})

    @task
    def create_resource(self):
        resource_name = generate_id()

        self.client.post("/api/v1/resources", headers=self.auth_header,
                         json={
                             'name': resource_name,
                             'cpu': '500m',
                             'memory': '1Gi',
                             'gpu': '0',
                             'cpuLimit': '500m',
                             'memoryLimit': '1Gi',
                             'gpuLimit': '0',
                         })

    @task
    def create_deployment(self):
        resource = random.choice(self.get_resources())
        model = random.choice(self.get_models())
        model_metadata = self.get_model_metadata(model)[-1]

        if model_metadata['status'] != 'SUCCEEDED':
            return

        self.client.post("/api/v1/deployments", headers=self.auth_header,
                         json={
                             'name': generate_id(),
                             'modelMetadataId': model_metadata['id'],
                             'strategy': 'rolling',
                             'resourceId': resource['id'],
                             'scale': {
                                 'standard': 'REPLICAS',
                                 'standardValue': "1",
                                 'minReplicas': 1,
                                 'maxReplicas': 1
                             }
                         })

    @task(20)
    def load_test_endpoint(self):
        deployment = random.choice(self.get_deployments())
        ep = deployment['endPoint']

        if deployment['status'] not in ['RUNNING', 'UNKNOWN']:
            return

        self.client.post(f"https://{ep}/predict", headers={"accept": 'text/plain', 'Content-Type': 'image/jpeg'}, data=open('images/leonberg.jpg', 'rb'))

    def delete_resource(self):
        self.client.delete(f"/api/v1/resources/{self.resource['id']}")

    def delete_deployment(self):
        self.client.delete(f"/api/v1/deployments/{self.deployment['id']}")
