# TaskFlow report notes

## Software description
TaskFlow is a browser-based task management application. Users can create tasks, assign categories, mark tasks complete or pending, and view aggregate statistics.

## Architecture
The Streamlit frontend is the presentation component. The FastAPI Task Service owns task CRUD operations and database access. The FastAPI Statistics Service calculates aggregate values by requesting task data from the Task Service. PostgreSQL provides persistence. Kubernetes Services provide stable internal names and load balancing, while the frontend NodePort provides external access.

## Cloud architecture principles
- Microservice separation of responsibilities
- Stateless application services
- REST-based synchronous communication
- Kubernetes service discovery
- Independent horizontal scaling
- External frontend / internal backend separation
- Persistent state separated from application containers
- Health checks and resource limits

## Benefits and challenges
The Task and Statistics services can be deployed and scaled independently. Stateless replicas can be replaced without losing task data because persistent state resides in PostgreSQL. Microservices also add network calls and deployment complexity. A production system would need stronger monitoring, failure handling, database backups and high availability.

## Security
Only the frontend is externally exposed. Backend APIs and PostgreSQL are ClusterIP services. Database configuration is injected using a Kubernetes Secret. Application containers run as non-root. Production improvements include TLS, authentication/authorization, NetworkPolicies, centralized secret management, image scanning, rate limiting, backups and audit logging.

## Business implications
TaskFlow is intentionally too small to justify microservices economically. The assumed scenario is a larger organization with many simultaneous users. Under that assumption, task operations and statistics can have different demand profiles, making independent scaling useful. The trade-off is greater operational complexity than a monolithic application.
