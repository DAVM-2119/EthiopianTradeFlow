from locust import HttpUser, task, between
import uuid

class TradeFlowShipperUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Authenticate Shipper
        resp = self.client.post("/api/v1/accounts/auth/token/", json={
            "email": "shipper1@tradeflow.et",
            "password": "Password123!"
        })
        if resp.status_code == 200:
            token = resp.json().get("access")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(3)
    def browse_loads(self):
        self.client.get("/api/v1/loads/")

    @task(1)
    def create_load(self):
        self.client.post("/api/v1/loads/", json={
            "title": f"Load {uuid.uuid4().hex[:6]}",
            "origin_city": "Djibouti Port",
            "destination_city": "Modjo Dry Port",
            "cargo_type": "CONTAINERIZED",
            "weight": "25.00",
            "pickup_window_start": "2026-09-01T08:00:00Z",
            "pickup_window_end": "2026-09-03T18:00:00Z"
        })


class TradeFlowTransporterUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        resp = self.client.post("/api/v1/accounts/auth/token/", json={
            "email": "transporter1@tradeflow.et",
            "password": "Password123!"
        })
        if resp.status_code == 200:
            token = resp.json().get("access")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(4)
    def list_marketplace_loads(self):
        self.client.get("/api/v1/loads/")

    @task(2)
    def check_my_bids(self):
        self.client.get("/api/v1/loads/my-bids/")


class TradeFlowDriverUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        resp = self.client.post("/api/v1/accounts/auth/token/", json={
            "email": "driver1@tradeflow.et",
            "password": "Password123!"
        })
        if resp.status_code == 200:
            token = resp.json().get("access")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task
    def post_gps_telemetry(self):
        self.client.post("/api/v1/tracking/events/", json={
            "shipment": "00000000-0000-0000-0000-000000000001",
            "latitude": 11.5883,
            "longitude": 43.1450,
            "speed": 60.0,
            "heading": 240.0,
            "recorded_at": "2026-09-01T10:00:00Z",
            "event_id": f"gps-{uuid.uuid4()}"
        })
