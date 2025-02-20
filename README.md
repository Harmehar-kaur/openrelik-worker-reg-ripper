# OpenRelik Worker - RegRipper

## Overview
The OpenRelik RegRipper Worker is a forensic tool designed to analyze Windows registry hive files using RegRipper within the OpenRelik framework. This worker automates the extraction and analysis of registry artifacts, making it easier for forensic investigators to process registry data.

## Usage
This worker is designed to be deployed as part of an OpenRelik environment. It detects the type of registry hive provided, runs RegRipper with the appropriate profile, and generates forensic reports as output files.

## Adding the Container as a Service
To run this worker as a service using Docker Compose, add the following service definition to your `docker-compose.yml`:

```yaml
  openrelik-regripper:
    image: openrelik/regripper-worker:latest
    container_name: openrelik-regripper
    restart: always
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ./data:/app/data
    command: "celery --app=src.app worker --task-events --concurrency=2 --loglevel=INFO -Q openrelik-worker-reg-ripper"

```

### Starting the Service
Once the service is defined in `docker-compose.yml`, run:
```bash
docker-compose up -d
```
This will start the worker container in the background and connect it to the OpenRelik network.

## Output
- **Text Report (`.txt`)**: Contains extracted registry information based on the hive type.
- **Log File (`.log`)**: Captures execution logs and potential errors.
