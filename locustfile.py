from locust import FastHttpUser, task
import uuid
import time


class So1sUser(FastHttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None
        self.model_metadata = None
        self.resource = None
        self.deployment = None

    @task
    def main_task(self):
        self.login()
        self.create_model()
        self.create_resource()
        self.create_deployment()
        self.load_test_endpoint()
        self.delete_deployment()
        self.delete_resource()
        self.delete_model()

    def login(self):
        self.client.post(
            "/api/v1/signin", json={"username": "so1s", "password": "admin12345"})

    def create_model(self):
        model_name = str(uuid.uuid4())

        self.client.post(
            "/api/v1/models", files=[  # https://superuser.com/a/960710/1159180
                ('modelFile', ('model.tgz', open('./models/efficientnet.tgz', 'rb'), 'application/gzip'))],

            json={"name": model_name,
                  'library': 'keras',
                  'inputShape': '(1,)',
                  'inputDType': 'numpy',
                  'outputShape': '(1,)',
                  'inputDType': 'numpy',
                  'deviceType': 'CPU'})

        models = self.client.get("/api/v1/models").json()
        self.model = [e for e in models if e["name"]
                      == model_name][0]

        while self.model_metadata is None or self.model_metadata.get('status') not in ['SUCCEEDED', 'FAILED']:
            self.model_metadata = self.client.get(
                f"/api/v1/models/{self.model['id']}").json()[0]
            time.sleep(0.5)

    def delete_model(self):
        self.client.delete(
            f"/api/v1/models/{self.model['id']}/versions/{self.model_metadata['version']}")

        time.sleep(1)

        self.client.delete(
            f"/api/v1/models/{self.model['id']}")

    def create_resource(self):
        resource_name = str(uuid.uuid4())

        self.client.post("/api/v1/resources", json={
            'name': resource_name,
            'cpu': '500m',
            'memory': '1Gi',
            'gpu': '0',
            'cpuLimit': '500m',
            'memoryLimit': '1Gi',
            'gpuLimit': '0',
        })

        time.sleep(1)

        resources = self.client.get("/api/v1/resources").json()

        self.resource = [e for e in resources if e['name'] == resource_name][0]

    def delete_resource(self):
        self.client.delete(f"/api/v1/resources/{self.resource['id']}")

    def create_deployment(self):
        self.client.post("/api/v1/deployments", json={
            'name': str(uuid.uuid4()),
            'modelMetadataId': self.model_metadata['id'],
            'strategy': 'rolling',
            'resourceId': self.resource['id'],
            'scale': {
                'standard': {
                    'unit': '',
                    'type': ''
                },
                'standardValue': 1,
                'minReplicas': 1,
                'maxReplicas': 1
            }
        })

    def delete_deployment(self):
        self.client.delete(f"/api/v1/deployments/{self.deployment['id']}")

    def load_test_endpoint(self):
        ep = self.deployment['endPoint']

        for i in range(int(10**5)):
            self.client.post(f"{ep}/predict", files=[
                ('image', ('leonberg.jpg', open('images/leonberg.jpg', 'rb'), 'image/jpeg'))])
