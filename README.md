# PII Redaction Service

A FastAPI service for redacting Personally Identifiable Information (PII) from text using spaCy NER.

## Features

- Redacts PII from text using custom-trained spaCy model
- Supports training with new data
- Evaluates model performance
- Docker support for easy deployment
- CI/CD pipeline with Jenkins integration
- Kubernetes deployment support

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Kubernetes cluster (for deployment)
- Jenkins (for CI/CD)

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn src.main:redact_app --reload
```

The service will be available at http://localhost:8000

## API Endpoints

### Redact PII
```
POST /redact
{
    "text": "string"
}
```

### Train Model
```
POST /train
{
    "training_data": [
        {
            "text": "string",
            "redacted_text": "string"
        }
    ],
    "iterations": 20
}
```

### Evaluate Model
```
POST /evaluate
{
    "test_data": [
        {
            "text": "string",
            "redacted_text": "string"
        }
    ]
}
```

Example payloads:

1. Basic evaluation:
```json
{
    "test_data": [
        {
            "text": "John Smith works at Google",
            "redacted_text": "[NAME] works at [ORGANIZATION]"
        },
        {
            "text": "Contact me at john.smith@example.com or +1 234 567 8900",
            "redacted_text": "Contact me at [EMAIL] or [PHONE_NUMBER]"
        }
    ]
}
```

2. With multiple categories:
```json
{
    "test_data": [
        {
            "text": "Sarah Thompson lives in Sydney, NSW",
            "redacted_text": "[NAME] lives in [ADDRESS], [ADDRESS]"
        },
        {
            "text": "The CEO of Microsoft is Satya, email: ceo@microsoft.com",
            "redacted_text": "The CEO of [ORGANIZATION] is [NAME], email: [EMAIL]"
        }
    ]
}
```

The endpoint returns evaluation metrics including:
- Precision
- Recall
- F1 Score
- Per-category metrics

### Health Check
```
GET /health
```

## Docker and Docker Compose

The service can be run using Docker Compose which provides a development environment with volume mounts for code and model persistence.

1. Start the service with Docker Compose:
```bash
docker-compose up --build
```

Key features of the Docker setup:
- Automatic code reloading during development
- Persistent model storage through Docker volumes
- Hot-reloading of source code via volume mounts
- Isolated Python environment with all dependencies

The service will be available at http://localhost:8000

### Volume Mounts
The Docker Compose setup includes the following volume mounts:
- `./src:/app/src`: Mounts the source code directory for hot-reloading
- `./models:/app/models`: Persists trained models across container restarts
- `./requirements.txt:/app/requirements.txt`: Ensures consistent dependency versions

Note: The `models` and `data` volumes are defined in the Docker Compose file to persist model and data files across container restarts.


## Model Training

To train the model for the first time:
Run `/train` endpoint without training data in payload so it will use the data from `/data/pii_data.json`

This will train the model and save it to `models/pii_ner` directory.

## CI/CD Pipeline Setup

1. Configure Jenkins credentials:
   - Docker registry credentials
   ```groovy
   docker-registry-credentials:
     - Username: your Docker registry username
     - Password: your Docker registry password
   ```
   
   - Kubernetes credentials
   ```groovy
   k8s-namespace:
     - String: your Kubernetes namespace
   
   k8s-context:
     - String: your Kubernetes context
   ```

2. Update Jenkinsfile configuration:
   - Set `DOCKER_REGISTRY` to your Docker registry URL
   - Update email address in failure notification

3. Configure Docker registry:
   - Ensure you have access to a Docker registry
   - Set up proper authentication

## Kubernetes Deployment

1. Deploy to Kubernetes:
```bash
kubectl apply -f k8s/deployment.yaml -n your-namespace
kubectl apply -f k8s/service.yaml -n your-namespace
```

2. Access the service:
   - Internal: `pii-redaction-service.your-namespace.svc.cluster.local:8000`
   - External: Use the LoadBalancer IP/hostname

## Monitoring

The service includes health checks that can be monitored:
- Liveness probe: `/health` endpoint
- Readiness probe: `/health` endpoint

## Error Handling

The service returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 500: Internal Server Error
- 503: Service Unavailable (health check failures)

## API Usage

Send a POST request to `/redact` with a JSON body containing the text to redact:

```bash
curl -X POST http://localhost:8000/redact \
  -H "Content-Type: application/json" \
  -d '{"text": "Please contact Sarah Thompson at sarah.thompson@company.com.au or 0422 111 222 to schedule a meeting."}'
```

Response:
```json
{
  "redacted_text": "Please contact [NAME] at [EMAIL] or [PHONE_NUMBER] to schedule a meeting."
}
```
