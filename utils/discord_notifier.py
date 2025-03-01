import logging
import requests


def send_discord_message(webhook_url, embeds):
    if not webhook_url:
        logging.warning("WEBHOOK_URL not set. Discord message not sent.")
        return
    try:
        response = requests.post(url=webhook_url, json={"embeds": embeds}, timeout=10)
        if response.status_code not in range(200, 299):
            logging.error(f"Error sending Discord message: {response.json()}")
        else:
            logging.info("Successfully sent Discord message.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Discord message failed: {e}")
