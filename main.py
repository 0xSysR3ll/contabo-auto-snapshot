# src/main.py
import logging
import os
import yaml
import time
from datetime import datetime
from dateutil.tz import tzlocal
from croniter import croniter
from utils.contabo_api import ContaboAPI
from utils.discord_notifier import send_discord_message


def load_config():
    # Load configuration from environment variables if set, otherwise from config file
    config = {
        "webhook_url": os.getenv("WEBHOOK_URL"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "api_user": os.getenv("API_USER"),
        "api_password": os.getenv("API_PASSWORD"),
        "cron_schedule": os.getenv("CRON_SCHEDULE"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Determine the path to the configuration file
    config_path = os.getenv("CONFIG_PATH", "config/config.yml")

    # Check if any configuration is missing and load from config file if available
    if any(value is None for value in config.values()):
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                file_config = yaml.safe_load(config_file)
                for _, value in config.items():
                    if value is None and _ in file_config:
                        config[_] = file_config[_]
        except FileNotFoundError:
            logging.warning(
                "Configuration file not found. Ensure all environment variables are set."
            )
    # Check if any configuration is still missing
    if any(value is None for value in config.values()):
        raise ValueError(
            "Missing configuration values. Please check your environment variables or configuration file."
        )
    return config


config = load_config()

WEBHOOK_URL = config["webhook_url"]
CLIENT_ID = config["client_id"]
CLIENT_SECRET = config["client_secret"]
API_USER = config["api_user"]
API_PASSWORD = config["api_password"]
CRON_SCHEDULE = config["cron_schedule"]
LOG_LEVEL = config["log_level"]

# Logging Configuration
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/auto-snapshots.log", encoding="utf-8"),
    ],
)


def auto_snapshots():
    api = ContaboAPI(CLIENT_ID, CLIENT_SECRET, API_USER, API_PASSWORD)
    instances = api.get_instances()
    for instance in instances:
        instance_name = instance["name"]
        instance_dsname = instance["displayName"]
        instance_id = instance["instanceId"]
        snapshots = api.get_snapshots(instance_id)
        if snapshots:
            oldest_snapshot = min(snapshots, key=lambda x: x["createdDate"])
            api.delete_snapshot(instance_id, oldest_snapshot["snapshotId"])

        snapshot = api.create_snapshot(instance_id)
        if not snapshot:
            # Failure embed
            embed = [
                {
                    "description": f"Failed to create a snapshot for instance `{instance_dsname} - {instance_name}({instance_id})`",
                    "fields": [
                        {
                            "name": "Instance ID",
                            "value": instance_id,
                            "inline": False,
                        },
                        {
                            "name": "Timestamp",
                            "value": datetime.now(tzlocal()).isoformat(),
                            "inline": False,
                        },
                    ],
                    "title": "Auto-snapshots BOT - Snapshot Creation Failed",
                    "thumbnail": {
                        "url": "https://auth.contabo.com/auth/resources/2rmpy/login/contabo/img/logo.png"
                    },
                    "timestamp": datetime.now(
                        tzlocal()
                    ).isoformat(),  # Use ISO 8601 format for the timestamp
                    "footer": {"text": "Made with ❤️ by 0xsysr3ll"},
                    "color": 0xE01B24,  # Red color to indicate failure
                }
            ]
            send_discord_message(WEBHOOK_URL, embed)
            logging.error(
                f"Failed to create a snapshot for instance {instance_dsname} - {instance_name}({instance_id}."
            )
            continue

        embed = [
            {
                "description": f"Successfully created a snapshot for instance `{instance_dsname} - {instance_name}({instance_id})`",
                "fields": [
                    {
                        "name": "Snapshot ID",
                        "value": snapshot[0]["snapshotId"],
                        "inline": False,
                    },
                    {"name": "Name", "value": snapshot[0]["name"], "inline": False},
                    {
                        "name": "Description",
                        "value": snapshot[0]["description"],
                        "inline": False,
                    },
                    {
                        "name": "Created at",
                        "value": snapshot[0]["createdDate"],
                        "inline": False,
                    },
                    {
                        "name": "Deleted at",
                        "value": snapshot[0]["autoDeleteDate"],
                        "inline": False,
                    },
                ],
                "title": "Auto-snapshots BOT result",
                "thumbnail": {
                    "url": "https://auth.contabo.com/auth/resources/2rmpy/login/contabo/img/logo.png"
                },
                "timestamp": datetime.now(
                    tzlocal()
                ).isoformat(),  # Use ISO 8601 format for the timestamp
                "footer": {"text": "Made with ❤️ by 0xsysr3ll"},
                "color": 0x26A269,  # Correct color format (integer, not string)
            }
        ]
        send_discord_message(WEBHOOK_URL, embed)


def schedule_auto_snapshots(cron_schedule):
    while True:
        now = datetime.now()
        cron = croniter(cron_schedule, now)
        next_run = cron.get_next(datetime)

        sleep_time = (next_run - now).total_seconds()
        logging.info(f"Next snapshot scheduled at {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        time.sleep(sleep_time)
        auto_snapshots()


if __name__ == "__main__":
    logging.info("Auto-snapshots BOT started.")
    schedule_auto_snapshots(CRON_SCHEDULE)
