# Auto-Snapshots Bot

Auto-Snapshots Bot is a Python application designed to automate the creation and management of snapshots for Contabo instances. It allows users to schedule snapshot creation using a cron-like syntax and supports configuration via environment variables or a configuration file.

## Features

- Automated snapshot creation for Contabo instances.
- Scheduling using cron syntax.
- Configurable via environment variables or a YAML configuration file.
- Notifications via Discord webhooks.
- Modular design for easy maintenance and extension.

## Prerequisites

- Docker and Docker Compose installed on your machine.
- Access to Contabo API with necessary credentials.

## Getting Started

### Configuration

Create a `config.yml` file in the `config` directory with the following content:

```yaml
webhook_url: "YOUR_DISCORD_WEBHOOK_URL"
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
api_user: "YOUR_API_USER"
api_password: "YOUR_API_PASSWORD"
cron_schedule: "0 0 * * *"  # Cron syntax for scheduling
log_level: "INFO"
```

Alternatively, you can set these values using environment variables.

### Building and Running with Docker Compose

```bash
docker compose build
docker compose up -d
```

### Environment Variables

You can override the configuration file settings using environment variables:

- `WEBHOOK_URL`: Discord webhook URL for notifications.
- `CLIENT_ID`: Contabo API client ID.
- `CLIENT_SECRET`: Contabo API client secret.
- `API_USER`: Contabo API user (email).
- `API_PASSWORD`: Contabo API password.
- `CRON_SCHEDULE`: Cron syntax for scheduling (e.g., `0 0 * * *` for daily at midnight).
- `LOG_LEVEL`: Logging level (e.g., `INFO` or `DEBUG`).

## Logging

Logs are stored in the logs directory. The application logs important events and errors to help with debugging and monitoring.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

Thanks to Contabo for providing the [API](https://api.contabo.com). \
Inspired by the need for automated snapshot management.