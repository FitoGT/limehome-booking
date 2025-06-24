# Limehome Backend Challenge

## Context

This repository contains a small service for handling bookings for Limehome's units. A booking maps a guest to a unit with arrival and stay duration details. Ensuring accurate booking coverage and maximizing occupancy are critical to our business.

**Note**: This README has been updated to reflect recent improvements, including bug fixes, a new extend-stay feature, and an enhanced architecture for better maintainability and reusability.


## Bug Fixes

- **Overlapping Bookings**: Previously, the system did not correctly prevent a new booking from overlapping with an existing one. We fixed this by:
  1. Persisting a `check_out_date` in the `Booking` model.
  2. Validating on booking creation that no existing booking for the same unit overlaps the requested period (`check_in_date` to `check_out_date`).


## New Feature: Extend Stay Endpoint
Added a new endpoint to allow guests to extend their stay, with full validation and clear error handling.


## How to run

### Prerequisutes

Make sure to have the following installed

- Python3
- git
- docker

### Setup

To get started, clone the repository locally and run the following

```shell
[~]$ docker-compose up
Attaching to fastapi-application
fastapi-application  | INFO:     Started server process [1]
fastapi-application  | INFO:     Waiting for application startup.
fastapi-application  | INFO:     Application startup complete.
fastapi-application  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
fastapi-application  | INFO:     192.168.112.1:64034 - "GET / HTTP/1.1" 200 OK
```

To make sure that everything is setup properly, open http://localhost:8000 in your browser and you should see an OK message.
The logs should be looking like this

```shell
fastapi-application  | INFO:     192.168.112.1:64034 - "GET /docs HTTP/1.1" 200 OK
```

To navigate to the swagger docs, open the url http://localhost:8000/docs , the logs should be looking like this

```shell
fastapi-application  | INFO:     192.168.112.1:64034 - "GET /openapi.json HTTP/1.1" 200 OK
```

### Running tests

Open your terminal and run the following commands in the cloned directory (ignore the failing test)

```shell
[~]$ source ./venv/bin/activate  # activate the virtual env shell
(venv)[~]$ pytest
platform win32 -- Python 3.10.11, pytest-7.3.1, pluggy-1.0.0
rootdir: C:\Users\adolf\limehome-booking\app
plugins: anyio-3.6.2, asyncio-0.21.0, freezegun-0.4.2
asyncio: mode=strict
collected 9 items

test_bookings.py .........
```


