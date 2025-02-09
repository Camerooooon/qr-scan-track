QR Scan Tracker
---

A self-hosted URL shortner that keeps track of device details for marketing purposes.

# Starting the website

Use `docker compose up` to automatically build and start the website on port 8080

# Environment variables

Set the environment variable `TRACKER_DATABASE_PATH` to the directory where you want to save the json database which contains the logs of click.

Set the environment variable `TRACKER_ADMIN_KEY` to the key that you want to use for authentication.

# API

`curl -X PUT localhost:8000/track/new_track -d https://example.com -H "X-API-Key: 123"` to create a new tracked shortened url.
