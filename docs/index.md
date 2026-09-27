# E-Commerce Order Processing System

## Architecture

This is an async, message-queue driven order processing system:

- **Order API** — FastAPI service that accepts new orders and publishes them to a queue
- **Order Worker** — Celery/pika worker that consumes orders and processes them (inventory check, payment, fulfillment)
- **MySQL** — persistent storage for orders and order status
- **RabbitMQ** — message broker connecting the API and worker
Client → Order API → RabbitMQ → Order Worker → MySQL

## How to Run Locally

1. Clone the repository
2. Start dependencies: `docker-compose up -d mysql rabbitmq`
3. Run the Order API: `uvicorn app.main:app --reload`
4. Run the Order Worker: `celery -A app.worker worker --loglevel=info`

## How to Deploy

The service is deployed to Kubernetes using the manifests in the `k8s/` directory:
kubectl apply -f k8s/

CI/CD is handled via GitHub Actions — see `.github/workflows/` for the pipeline definition.
