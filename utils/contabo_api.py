import logging
import requests
from datetime import datetime
from uuid import uuid4


class ContaboAPI:
    def __init__(self, client_id, client_secret, api_user, api_password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_user = api_user
        self.api_password = api_password
        self.access_token = None
        self.instances = {}
        self.connect()

    def connect(self):
        logging.info("Connecting to Contabo API...")
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": self.api_user,
            "password": self.api_password,
        }
        try:
            response = requests.post(
                url="https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token",
                data=data,
                timeout=10,
            )
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            if not self.access_token:
                logging.error("Failed to obtain access token.")
                raise Exception("Authentication failed")
        except requests.exceptions.RequestException as e:
            logging.error(f"Connection to Contabo API failed: {e}")
            raise

    def api_call(self, method, endpoint, **kwargs):
        url = f"https://api.contabo.com/v1/compute/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-request-id": str(uuid4()),
            "Content-Type": "application/json",
        }
        if method == "DELETE":
            headers.pop("Content-Type", None)
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            if method == "DELETE":
                return
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API call to {url} failed: {e}")
            return None

    def get_instances(self):
        logging.info("Fetching instances...")
        data = self.api_call("GET", "instances")
        self.instances = data.get("data", [])
        if not self.instances:
            logging.warning("No instances found.")
        return self.instances

    def get_snapshots(self, instance_id):
        logging.info(f"Fetching snapshots for instance {instance_id}...")
        data = self.api_call("GET", f"instances/{instance_id}/snapshots")
        return data.get("data", []) if data else []

    def create_snapshot(self, instance_id, name=None, description="Auto-snapshots BOT"):
        logging.info(f"Creating snapshot for instance {instance_id}...")
        name = name or datetime.now().strftime("%Y%m%d-%H%M%S")
        data = {"name": name, "description": description}
        response = self.api_call(
            "POST", f"instances/{instance_id}/snapshots", json=data
        )
        if response:
            logging.info(f"Snapshot created: {response['data'][0]['snapshotId']}")
            return response["data"]
        return []
    def delete_snapshot(self, instance_id, snapshot_id):
        logging.info(f"Deleting snapshot {snapshot_id} for instance {instance_id}...")
        self.api_call("DELETE", f"instances/{instance_id}/snapshots/{snapshot_id}")