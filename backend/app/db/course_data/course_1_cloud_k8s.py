from app.db.course_data.helpers import make_lesson, make_question

# Course 1: Cloud Architecture & Kubernetes at Scale
# Slug: cloud-architecture-kubernetes-scale

MODULE_1_LESSONS = [
    make_lesson(
        title="Cloud Computing Fundamentals",
        slug="cloud-computing-fundamentals",
        order_index=1,
        duration_minutes=45,
        description="Introduction to core cloud computing concepts, delivery models, elasticity, and shared responsibility.",
        objectives=[
            "Understand the NIST definition and key characteristics of cloud computing",
            "Differentiate between public, private, hybrid, and multi-cloud strategies",
            "Analyze the Shared Responsibility Model across different cloud layers"
        ],
        content_body="""Cloud computing is the on-demand delivery of compute power, database storage, applications, and other IT resources via the internet with pay-as-you-go pricing.

### The Five Essential Characteristics (NIST)
1. **On-demand self-service**: Provision compute resources automatically without human intervention from the provider.
2. **Broad network access**: Capabilities are accessible over standard network mechanisms across diverse client platforms.
3. **Resource pooling**: Provider computing resources are pooled to serve multiple consumers using multi-tenancy.
4. **Rapid elasticity**: Capabilities can be elastically provisioned and released to scale outward and inward with demand.
5. **Measured service**: Resource usage is monitored, controlled, and reported transparently for both provider and consumer.

### The Shared Responsibility Model
Security and compliance are shared between the cloud provider and the customer:
- **Cloud Provider ("Security OF the Cloud")**: Physical data centers, host hardware, virtualization hypervisor, networking infrastructure.
- **Customer ("Security IN the Cloud")**: Customer data, identity and access management (IAM), operating system patches (for IaaS), network firewalls, and application code.""",
        key_concepts=[
            "On-demand self-service and multi-tenancy",
            "Elastic scaling vs static provisioning",
            "Shared Responsibility Model across IaaS/PaaS/SaaS",
            "Total Cost of Ownership (TCO) and Capital vs Operational Expenditures"
        ],
        practical_example="""```bash
# Example AWS CLI command demonstrating on-demand elasticity and automation
aws ec2 run-instances \\
    --image-id ami-0c55b159cbfafe1f0 \\
    --instance-type t3.micro \\
    --key-name ProductionKeyPair \\
    --security-group-ids sg-0123456789abcdef0 \\
    --subnet-id subnet-0123456789abcdef0 \\
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Environment,Value=Production}]'
```""",
        completion_req="Read all lesson materials and review the shared responsibility boundaries.",
        is_free_preview=True
    ),
    make_lesson(
        title="IaaS, PaaS and SaaS",
        slug="iaas-paas-and-saas",
        order_index=2,
        duration_minutes=50,
        description="Comprehensive analysis of cloud service models: Infrastructure as a Service, Platform as a Service, and Software as a Service.",
        objectives=[
            "Distinguish between IaaS, PaaS, and SaaS architectural boundaries",
            "Evaluate operational overhead and trade-offs for each service tier",
            "Select appropriate deployment models based on enterprise requirements"
        ],
        content_body="""The cloud computing spectrum spans three fundamental service tiers, each offering different levels of abstraction, control, and management overhead.

### 1. Infrastructure as a Service (IaaS)
Provides fundamental computing resources (virtual machines, software-defined networks, block/object storage).
- *Customer controls*: Operating system, runtime, middleware, applications, data.
- *Examples*: AWS EC2, GCP Compute Engine, Azure Virtual Machines.

### 2. Platform as a Service (PaaS)
Abstracts hardware and operating system management, providing a pre-configured execution platform.
- *Customer controls*: Application code, configurations, data.
- *Examples*: AWS Elastic Beanstalk, Google App Engine / Cloud Run, Heroku.

### 3. Software as a Service (SaaS)
Delivers complete, centrally hosted end-user applications over the web.
- *Customer controls*: Application configuration, user access, data governance.
- *Examples*: Google Workspace, Microsoft 365, Salesforce.""",
        key_concepts=[
            "Abstraction tiers and maintenance burden",
            "Control vs convenience tradeoffs",
            "Vendor lock-in implications across PaaS vs IaaS",
            "Cost models: compute-hour vs usage-tier pricing"
        ],
        practical_example="""```yaml
# PaaS Deployment Configuration (Google Cloud Run / App Engine app.yaml)
runtime: python311
instance_class: F2
automatic_scaling:
  min_instances: 2
  max_instances: 10
  target_cpu_utilization: 0.65
env_variables:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
```""",
        completion_req="Analyze the operational boundaries between IaaS, PaaS, and SaaS."
    ),
    make_lesson(
        title="Cloud Architecture Patterns",
        slug="cloud-architecture-patterns",
        order_index=3,
        duration_minutes=55,
        description="Architectural design patterns for high availability, fault tolerance, scalability, and disaster recovery in the cloud.",
        objectives=[
            "Master cloud design patterns: Circuit Breaker, CQRS, Event Sourcing, and Cache-Aside",
            "Design multi-region and multi-zone resilient architectures",
            "Calculate Recovery Time Objective (RTO) and Recovery Point Objective (RPO)"
        ],
        content_body="""Modern cloud-native systems require deliberate architectural patterns to handle distributed network failures, sudden load spikes, and partial outages gracefully.

### Key Resiliency Patterns
- **Circuit Breaker**: Prevents an application from repeatedly attempting an operation that's likely to fail, returning a graceful fallback.
- **Cache-Aside (Lazy Loading)**: Loads data on-demand into cache when requested, reducing database latency and contention.
- **CQRS (Command Query Responsibility Segregation)**: Separates read and write operations into distinct data models and optimized datastores.
- **Bulkhead Pattern**: Isolates resources (connection pools, memory pools) into distinct partitions to prevent single failures from cascading.

### Disaster Recovery Strategies
1. *Backup & Restore*: Low cost, high RTO/RPO.
2. *Pilot Light*: Core data synchronized, minimal compute running.
3. *Warm Standby*: Scaled-down replica running in secondary region.
4. *Multi-Region Active-Active*: Zero downtime, real-time bidirectional replication.""",
        key_concepts=[
            "Fault isolation domains (Availability Zones and Regions)",
            "Idempotency and graceful degradation",
            "RTO vs RPO metrics",
            "Distributed state management"
        ],
        practical_example="""```python
import time

class CircuitBreakerOpenException(Exception):
    pass

class SimpleCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def execute(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit is open; calls blocked")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e
```""",
        completion_req="Understand and implement resilience patterns like Circuit Breaker."
    ),
    make_lesson(
        title="Microservices Architecture",
        slug="microservices-architecture",
        order_index=4,
        duration_minutes=60,
        description="Deconstructing monolithic applications into loosely coupled, independently deployable microservices.",
        objectives=[
            "Apply Domain-Driven Design (DDD) to define Bounded Contexts",
            "Evaluate synchronous (REST/gRPC) vs asynchronous (EDA) communication",
            "Implement distributed tracing and API Gateway orchestration"
        ],
        content_body="""Microservices decompose applications into modular, discrete services that model specific business capabilities. Each microservice manages its own persistence and communicates via standardized network protocols.

### Architectural Principles
1. **Single Responsibility**: Each service is focused on a single business domain.
2. **Decentralized Data Management**: Each service owns its database (Database-per-Service pattern) to avoid tight schema coupling.
3. **API Contracts**: Services interact solely via well-defined REST, gRPC, or messaging contracts.
4. **Independent Deployability**: Changes in one service do not require synchronized deployments of other services.

### Microservices Challenges & Solutions
- *Distributed Transactions*: Solved with the Saga Pattern (orchestrated or choreographed compensation transactions).
- *Network Latency & Discovery*: Solved with API Gateways and Service Meshes (Envoy, Istio).
- *Observability*: Distributed tracing with OpenTelemetry (W3C Trace Context headers).""",
        key_concepts=[
            "Bounded Contexts and domain decomposition",
            "Database-per-service vs shared database anti-pattern",
            "Saga pattern for distributed consistency",
            "API Gateway pattern and Reverse Proxies"
        ],
        practical_example="""```json
// Example Distributed Tracing HTTP Headers (W3C TraceContext standard)
{
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "tracestate": "congo=t61rcWkgMzE,rojo=00f067a"
}
```""",
        completion_req="Complete the microservices architecture concepts and patterns study."
    ),
    make_lesson(
        title="Containers and Containerization",
        slug="containers-and-containerization",
        order_index=5,
        duration_minutes=50,
        description="Deep dive into Linux namespaces, cgroups, Union File Systems, and the OCI standard.",
        objectives=[
            "Explain the low-level Linux kernel primitives enabling containers (Namespaces, cgroups)",
            "Compare virtual machines (Type 1/Type 2 hypervisors) with OS-level virtualization",
            "Understand the OCI (Open Container Initiative) image and runtime specifications"
        ],
        content_body="""Containers provide lightweight, portable operating system virtualization by sharing the host kernel while isolating user space processes.

### Linux Kernel Primitives
- **Namespaces (Isolation)**:
  - `pid`: Process IDs
  - `net`: Network devices, ports, routes
  - `mnt`: Mount points and file systems
  - `ipc`: Inter-process communication
  - `uts`: Hostname and NIS domain
  - `user`: User and group IDs
- **Control Groups (cgroups - Resource Limiting)**: Restrict and monitor CPU, memory, disk I/O, and network bandwidth per container.
- **OverlayFS (Layering)**: Layered copy-on-write filesystem combining read-only image layers with a thin writable container layer.

### Virtual Machines vs Containers
- *VMs*: Virtualize physical hardware; each VM runs a full guest operating system; heavy resource footprint (GBs), minutes to boot.
- *Containers*: Virtualize the operating system kernel; share host kernel; lightweight (MBs), milliseconds to boot.""",
        key_concepts=[
            "Linux Namespaces (PID, NET, MNT, IPC, UTS, USER)",
            "cgroups v1 and v2 resource constraints",
            "UnionFS and Copy-on-Write (CoW) image layers",
            "OCI image format and containerd/runc runtime"
        ],
        practical_example="""```bash
# Inspecting Linux namespaces and cgroups on Linux
ls -la /proc/$$/ns/
cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```""",
        completion_req="Understand Linux containerization primitives and OCI architecture."
    ),
    make_lesson(
        title="Docker Fundamentals",
        slug="docker-fundamentals",
        order_index=6,
        duration_minutes=60,
        description="Practical containerization: Dockerfiles, multi-stage builds, networking, volumes, and security hardening.",
        objectives=[
            "Write secure, optimized, multi-stage Dockerfiles",
            "Manage container networking (bridge, host, overlay)",
            "Persist container data with named volumes and bind mounts"
        ],
        content_body="""Docker is the industry-standard developer toolset and runtime for building, shipping, and running containerized applications.

### Best Practices for Production Dockerfiles
1. **Multi-Stage Builds**: Separate build-time dependencies (compilers, SDKs) from the minimal production runtime image.
2. **Least Privilege**: Never run container processes as root. Use dedicated non-root users (`USER appuser`).
3. **Layer Caching Optimization**: Copy dependency manifests (`package.json`, `requirements.txt`) before application code so layer caches invalidate only on dependency updates.
4. **Minimal Base Images**: Use `alpine` or distroless images to reduce attack surfaces and vulnerability counts.""",
        key_concepts=[
            "Multi-stage Docker build pipelines",
            "Layer caching and image size minimization",
            "Non-root container execution security",
            "Docker networks: bridge, host, overlay, macvlan"
        ],
        practical_example="""```dockerfile
# Multi-Stage Build Example for a Production Python/FastAPI Application
FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runtime

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY . /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```""",
        completion_req="Build and run a multi-stage Docker container."
    ),
    make_lesson(
        title="Container Orchestration Overview",
        slug="container-orchestration-overview",
        order_index=7,
        duration_minutes=55,
        description="The necessity of container orchestration: scheduling, service discovery, self-healing, rolling updates, and comparison of platforms.",
        objectives=[
            "Understand why container orchestrators are required at scale",
            "Evaluate core orchestrator capabilities: scheduling, self-healing, load balancing",
            "Compare Kubernetes with Docker Swarm, Nomad, and ECS"
        ],
        content_body="""While running individual containers is straightforward, running thousands of microservices across clusters of physical and virtual servers requires automated orchestration.

### Core Responsibilities of an Orchestrator
- **Scheduling**: Intelligently placing containers on compute nodes based on resource availability, affinity/anti-affinity, and constraints.
- **Self-Healing**: Automatically restarting crashed containers, replacing unresponsive nodes, and re-routing traffic.
- **Service Discovery & Load Balancing**: Providing stable DNS endpoints and balancing traffic across ephemeral container replicas.
- **Declarative State & Rollouts**: Gradually rolling out new image versions with zero downtime and automatic rollback on failure.""",
        key_concepts=[
            "Imperative vs Declarative configuration",
            "Reconciliation loops and desired state management",
            "Automated health checks: liveness vs readiness probes",
            "Cluster node management and workload placement"
        ],
        practical_example="""```bash
# Example Docker Swarm command showing declarative service creation
docker service create \\
  --name web-app \\
  --replicas 5 \\
  --publish 80:80 \\
  --update-parallelism 2 \\
  --update-delay 10s \\
  nginx:alpine
```""",
        completion_req="Complete the overview of container orchestration systems."
    ),
    make_lesson(
        title="Cloud Storage and Database Fundamentals",
        slug="cloud-storage-and-database-fundamentals",
        order_index=8,
        duration_minutes=55,
        description="Cloud persistence: Block storage, File storage, Object storage, Relational databases, and NoSQL stores.",
        objectives=[
            "Differentiate Block, File, and Object Storage mechanisms and performance profiles",
            "Evaluate ACID relational databases vs BASE NoSQL stores",
            "Design tiered storage and lifecycle policies for cost efficiency"
        ],
        content_body="""Cloud persistence architectures require selecting the appropriate storage tier and database technology to match access patterns, consistency requirements, and latency budgets.

### Cloud Storage Types
- **Block Storage (e.g., AWS EBS, GCP Persistent Disk)**: Raw unformatted volumes attached directly to compute instances; ideal for databases and operating systems.
- **File Storage (e.g., AWS EFS, GCP Filestore)**: Managed NFS/SMB file systems shared concurrently across multiple compute instances.
- **Object Storage (e.g., AWS S3, GCP Cloud Storage)**: Highly durable (99.999999999% 11 9s), flat namespace storage accessed via REST APIs; ideal for static assets, backups, and big data lakes.

### Database Selection: SQL vs NoSQL
- *Relational (PostgreSQL, MySQL)*: Structured schema, ACID transactions, complex joins, vertical scaling.
- *Document (MongoDB, Couchbase)*: Semi-structured JSON, schema flexibility, document nesting.
- *Key-Value (Redis, DynamoDB)*: Ultra-low sub-millisecond latency, simple partition key lookups.
- *Columnar (Cassandra, Bigtable)*: High-throughput time-series and analytical queries at petabyte scale.""",
        key_concepts=[
            "Block vs File vs Object storage models",
            "11 9s durability and object lifecycle rules",
            "ACID vs BASE transactional models",
            "CAP theorem trade-offs in cloud datastores"
        ],
        practical_example="""```json
// Example S3 Lifecycle Configuration Policy for automated tiering
{
  "Rules": [
    {
      "ID": "MoveLogsToColdStorage",
      "Status": "Enabled",
      "Filter": { "Prefix": "logs/" },
      "Transitions": [
        { "Days": 30, "StorageClass": "STANDARD_IA" },
        { "Days": 90, "StorageClass": "GLACIER" }
      ],
      "Expiration": { "Days": 365 }
    }
  ]
}
```""",
        completion_req="Understand cloud storage paradigms and database trade-offs."
    )
]

MODULE_2_LESSONS = [
    make_lesson(
        title="Introduction to Kubernetes Architecture",
        slug="introduction-to-kubernetes-architecture",
        order_index=1,
        duration_minutes=60,
        description="Comprehensive overview of Kubernetes architecture, master-worker topologies, and the declarative control loop.",
        objectives=[
            "Understand Kubernetes architecture and core responsibilities",
            "Differentiate the Control Plane components from Worker Node components",
            "Explain the declarative reconciliation loop paradigm"
        ],
        content_body="""Kubernetes (k8s) is an open-source container orchestration system for automating application deployment, scaling, and management.

### Architectural Philosophy
Kubernetes operates on a **declarative model**: you declare the desired state in YAML/JSON manifests, and Kubernetes controllers continuously act to align the actual state with the desired state through a **reconciliation loop**.

### Control Plane vs Worker Nodes
- **Control Plane**: Makes global decisions about the cluster (scheduling, event detection, cluster state storage).
- **Worker Nodes**: Host the Pods that run your containerized application workloads and execute network/storage instructions.""",
        key_concepts=[
            "Declarative configuration vs imperative commands",
            "Control Plane and Worker Node separation",
            "Continuous reconciliation loop (`actual_state == desired_state`)",
            "Kubernetes API primitives and resource models"
        ],
        practical_example="""```bash
# Checking cluster component health and node states
kubectl get nodes -o wide
kubectl cluster-info
kubectl get componentstatuses
```""",
        completion_req="Review Kubernetes architecture components and node roles.",
        is_free_preview=True
    ),
    make_lesson(
        title="Kubernetes Control Plane Components",
        slug="kubernetes-control-plane-components",
        order_index=2,
        duration_minutes=65,
        description="In-depth breakdown of kube-apiserver, etcd, kube-scheduler, and kube-controller-manager.",
        objectives=[
            "Analyze the role of kube-apiserver as the single communication gateway",
            "Understand etcd distributed consensus (Raft) and consistency guarantees",
            "Examine kube-scheduler scoring/filtering algorithms and controller loops"
        ],
        content_body="""The Kubernetes Control Plane consists of four primary software components that govern the entire lifecycle of cluster objects.

### 1. kube-apiserver
The central REST API frontend for Kubernetes. All administrative commands (`kubectl`), worker nodes, and controllers communicate exclusively through the API server. It handles authentication, authorization (RBAC), admission control, and writes state to etcd.

### 2. etcd
A distributed, consistent, highly available key-value store implementing the Raft consensus algorithm. It holds the authoritative source of truth for all Kubernetes cluster state.

### 3. kube-scheduler
Watches for newly created Pods without assigned nodes and selects the optimal node based on resource requirements, hardware/software constraints, affinity/anti-affinity specifications, and taints/tolerations.

### 4. kube-controller-manager
Runs controller processes in a single binary, including Node Controller, Replication Controller, Endpoints Controller, and ServiceAccount Controller.""",
        key_concepts=[
            "kube-apiserver admission controllers and RBAC evaluation",
            "etcd Raft quorum and snapshotting",
            "kube-scheduler filtering (predicates) and scoring (priorities)",
            "controller-manager feedback loops"
        ],
        practical_example="""```bash
# Taking an etcd backup snapshot on the control plane
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \\
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \\
  --cert=/etc/kubernetes/pki/etcd/server.crt \\
  --key=/etc/kubernetes/pki/etcd/server.key \\
  snapshot save /tmp/etcd-backup.db
```""",
        completion_req="Understand each control plane component's role and failure modes."
    ),
    make_lesson(
        title="Pods, ReplicaSets, and Deployments",
        slug="pods-replicasets-and-deployments",
        order_index=3,
        duration_minutes=60,
        description="Workload primitives: Pod lifecycle, multi-container pods, ReplicaSets, and zero-downtime rolling updates with Deployments.",
        objectives=[
            "Define the Pod as the fundamental unit of deployment in Kubernetes",
            "Implement multi-container design patterns (sidecar, initContainer, adapter)",
            "Manage zero-downtime rolling updates and rollbacks using Deployments"
        ],
        content_body="""In Kubernetes, applications run inside **Pods**, the smallest deployable computing units that encapsulate one or more tightly coupled containers sharing network and storage namespaces.

### Pod Multi-Container Patterns
- **Init Containers**: Run to completion before app containers start (e.g., database schema migrations, downloading configuration).
- **Sidecar Containers**: Run alongside the primary container to enhance functionality (e.g., logging agents, Envoy proxy, metrics scrapers).

### Workload Abstractions
- **ReplicaSet**: Ensures a specified number of identical Pod replicas are running at all times using label selectors.
- **Deployment**: High-level declarative manager for ReplicaSets and Pods; enables rolling updates, pausing, and rollbacks.""",
        key_concepts=[
            "Pod lifecycle states (Pending, Running, Succeeded, Failed)",
            "Shared IPC and localhost networking in Pods",
            "RollingUpdate vs Recreate deployment strategies",
            "MaxSurge and MaxUnavailable parameters"
        ],
        practical_example="""```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-deployment
  labels:
    app: web-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```""",
        completion_req="Create and deploy a Kubernetes Deployment with a RollingUpdate strategy."
    ),
    make_lesson(
        title="Kubernetes Services and Networking",
        slug="kubernetes-services-and-networking",
        order_index=4,
        duration_minutes=65,
        description="Service abstraction, ClusterIP, NodePort, LoadBalancer, Headless Services, CoreDNS, and kube-proxy iptables/IPVS.",
        objectives=[
            "Explain Kubernetes flat networking model and IP-per-Pod philosophy",
            "Configure ClusterIP, NodePort, and LoadBalancer Services",
            "Understand kube-proxy packet filtering and CoreDNS service discovery"
        ],
        content_body="""Because Pods are ephemeral with dynamic IP addresses, Kubernetes provides the **Service** abstraction to expose a stable virtual IP (ClusterIP) and DNS name for a set of Pods matching a label selector.

### Service Types
1. **ClusterIP (Default)**: Exposes the Service on an internal IP reachable only within the cluster.
2. **NodePort**: Exposes the Service on each Node's IP at a static port (30000-32767).
3. **LoadBalancer**: Provisions an external cloud load balancer (e.g., AWS NLB, GCP Cloud LB) routing to the NodePort.
4. **Headless (None)**: Does not allocate a virtual ClusterIP; returns direct A/AAAA DNS records of matching Pod IPs (used for StatefulSets).

### Networking Implementation
- **kube-proxy**: Manages iptables or IPVS rules on each worker node to translate ClusterIPs to backing Pod IPs.
- **CoreDNS**: Resolves internal cluster domain names like `<service-name>.<namespace>.svc.cluster.local`.""",
        key_concepts=[
            "Container Network Interface (CNI) plugins (Calico, Cilium, Flannel)",
            "Stable DNS discovery and virtual ClusterIP",
            "kube-proxy iptables vs IPVS mode performance",
            "Endpoints and EndpointSlices"
        ],
        practical_example="""```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-api-service
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: backend-api
  ports:
  - name: http
    port: 8080
    targetPort: 8000
    protocol: TCP
```""",
        completion_req="Configure and verify Kubernetes Service routing and DNS resolution."
    ),
    make_lesson(
        title="Ingress Controllers and Gateways",
        slug="ingress-controllers-and-gateways",
        order_index=5,
        duration_minutes=60,
        description="Layer 7 routing, HTTP/HTTPS path and host-based routing, SSL/TLS termination, and the Kubernetes Gateway API.",
        objectives=[
            "Differentiate Layer 4 (Service) from Layer 7 (Ingress) routing",
            "Configure Ingress resources with host-based and path-based routing",
            "Implement automated TLS certificates with cert-manager and Let's Encrypt"
        ],
        content_body="""While Services operate at Layer 4 (TCP/UDP), **Ingress** and the modern **Gateway API** operate at Layer 7 (HTTP/HTTPS), managing external access, SSL termination, and URL routing rules into the cluster.

### Ingress Architecture
An Ingress resource requires an **Ingress Controller** (e.g., Ingress-NGINX, Traefik, HAProxy, Emissary-ingress) running in the cluster to watch Ingress rules and translate them into reverse-proxy configurations.

### Key Ingress Capabilities
- **Host-based routing**: Route traffic based on domain (e.g., `api.example.com` vs `app.example.com`).
- **Path-based routing**: Route traffic based on URI path (e.g., `/api/v1` vs `/static`).
- **TLS Termination**: Decrypt HTTPS traffic at the edge using Kubernetes Secrets.""",
        key_concepts=[
            "Layer 7 HTTP reverse proxy vs Layer 4 load balancing",
            "IngressClass and Ingress Controller daemon/deployment",
            "TLS termination and cert-manager ACME issuers",
            "Kubernetes Gateway API: GatewayClass, Gateway, HTTPRoute"
        ],
        practical_example="""```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: enterprise-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - lms.enterprise.com
    secretName: lms-tls-secret
  rules:
  - host: lms.enterprise.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```""",
        completion_req="Define and test an Ingress resource with path routing and TLS."
    ),
    make_lesson(
        title="ConfigMaps and Secrets Management",
        slug="configmaps-and-secrets-management",
        order_index=6,
        duration_minutes=55,
        description="Decoupling configuration and sensitive data from container images using ConfigMaps, Secrets, External Secrets, and HashiCorp Vault.",
        objectives=[
            "Create and inject ConfigMaps as environment variables and mounted files",
            "Securely manage Kubernetes Secrets with encryption at rest and RBAC",
            "Integrate enterprise secret stores using External Secrets Operator (ESO)"
        ],
        content_body="""The Twelve-Factor App methodology mandates strict separation of config from code. Kubernetes provides **ConfigMaps** for non-confidential configuration and **Secrets** for sensitive credentials (API keys, passwords, certificates).

### Consumption Methods
1. **Environment Variables**: Injected at container startup (`env` or `envFrom`). Note: changes do not hot-reload without container restart.
2. **Volume Mounts**: Mounted as files in the container filesystem. Updates to ConfigMaps/Secrets are automatically propagated into mounted files by kubelet.

### Production Secrets Best Practices
- Enable **Encryption at Rest** in `kube-apiserver` (using KMS providers like AWS KMS or HashiCorp Vault).
- Use tools like **External Secrets Operator (ESO)** or **Sealed Secrets** to prevent committing raw Base64 Secrets to Git.""",
        key_concepts=[
            "Decoupling configuration from container images",
            "ConfigMap and Secret injection (env vs volume mounts)",
            "Secret encryption at rest with KMS",
            "GitOps secret workflows: External Secrets Operator and SealedSecrets"
        ],
        practical_example="""```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  config.json: |
    {
      "feature_flags": { "new_dashboard": true },
      "timeout_seconds": 30
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  DB_PASSWORD: "SuperSecureProductionPassword123!"
```""",
        completion_req="Inject configuration and secrets into a workload via environment and volume."
    ),
    make_lesson(
        title="Persistent Volumes and Storage",
        slug="persistent-volumes-and-storage",
        order_index=7,
        duration_minutes=65,
        description="Stateful workloads: PersistentVolumes (PV), PersistentVolumeClaims (PVC), StorageClasses, Dynamic Provisioning, and StatefulSets.",
        objectives=[
            "Explain the PV and PVC binding lifecycle and abstraction layer",
            "Configure StorageClasses with CSI drivers for dynamic provisioning",
            "Deploy stateful clustered databases using StatefulSets"
        ],
        content_body="""While container filesystems are ephemeral by default, stateful applications (databases, caches, message queues) require data persistence beyond Pod restarts and node rescheduling.

### Storage Primitives
- **PersistentVolume (PV)**: A piece of storage in the cluster provisioned by an administrator or dynamically via a StorageClass.
- **PersistentVolumeClaim (PVC)**: A request for storage by a user/Pod specifying access modes (`ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`) and size.
- **StorageClass**: Defines the provisioner (AWS EBS, GCP PD, Ceph) and volume parameters for automated dynamic provisioning.

### StatefulSets
Used for stateful applications requiring:
- Stable, unique network identifiers (`db-0`, `db-1`, `db-2`).
- Ordered, graceful deployment and scaling.
- Dedicated persistent storage per replica via `volumeClaimTemplates`.""",
        key_concepts=[
            "PersistentVolume vs PersistentVolumeClaim binding",
            "Dynamic provisioning using StorageClasses and CSI drivers",
            "Access Modes: ReadWriteOnce (RWO), ReadOnlyMany (ROX), ReadWriteMany (RWX)",
            "StatefulSet volumeClaimTemplates and headless service integration"
        ],
        practical_example="""```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-cluster
spec:
  serviceName: "postgres-headless"
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        volumeMounts:
        - name: pg-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: pg-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "gp3"
      resources:
        requests:
          storage: 50Gi
```""",
        completion_req="Provision dynamic persistent volumes and bind them to stateful workloads."
    ),
    make_lesson(
        title="Helm Charts and Package Management",
        slug="helm-charts-and-package-management",
        order_index=8,
        duration_minutes=60,
        description="Managing complex Kubernetes deployments using Helm package manager, Go templating, values files, and chart repositories.",
        objectives=[
            "Structure Helm charts with Chart.yaml, templates, and values.yaml",
            "Utilize Go templating, functions, and control flow in manifests",
            "Manage releases, rollbacks, and multi-environment values overrides"
        ],
        content_body="""Helm is the de facto package manager for Kubernetes. Helm packages multiple related Kubernetes resources into versioned, reusable bundles called **Charts**.

### Helm Architecture & Concepts
- **Chart**: A collection of templated YAML files describing a set of Kubernetes resources.
- **Values (`values.yaml`)**: Configuration parameters injected into templates at release time.
- **Release**: A running instance of a chart in a Kubernetes cluster.
- **Helm CLI**: Client-side tool that renders templates locally and submits manifests to `kube-apiserver`.

### Advanced Templating
Helm uses Go text templates with Sprig helper functions:
- Built-in objects: `.Values`, `.Release`, `.Chart`, `.Template`.
- Flow control: `if/else`, `range`, `with`.
- Named templates (`_helpers.tpl`) for reusable snippet definitions.""",
        key_concepts=[
            "Helm chart directory structure and Chart.yaml metadata",
            "Go template syntax, pipelines, and Sprig functions",
            "Values hierarchy and multi-environment overrides (`-f values-prod.yaml`)",
            "Helm lifecycle hooks and rollback management"
        ],
        practical_example="""```yaml
# templates/deployment.yaml in a Helm Chart
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mychart.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
```""",
        completion_req="Create, lint, template, and deploy a custom Helm chart."
    ),
    make_lesson(
        title="Scaling and Autoscaling (HPA/VPA)",
        slug="scaling-and-autoscaling-hpa-vpa",
        order_index=9,
        duration_minutes=65,
        description="Dynamic workload scaling: Horizontal Pod Autoscaler (HPA), Vertical Pod Autoscaler (VPA), Cluster Autoscaler, and Karpenter.",
        objectives=[
            "Configure Horizontal Pod Autoscaler (HPA) for CPU, memory, and custom metrics",
            "Implement Vertical Pod Autoscaler (VPA) for resource rightsizing",
            "Understand Node-level autoscaling with Cluster Autoscaler and Karpenter"
        ],
        content_body="""Autoscaling in Kubernetes operates across two dimensions: **Workload Scaling** (adjusting Pod counts or sizes) and **Infrastructure Scaling** (adjusting Node counts).

### 1. Horizontal Pod Autoscaler (HPA)
Automatically scales the number of Pod replicas based on observed CPU/memory metrics or custom Prometheus metrics (via Prometheus Adapter or KEDA).
- Evaluation algorithm: `desiredReplicas = ceil[currentReplicas * (currentMetricValue / targetMetricValue)]`

### 2. Vertical Pod Autoscaler (VPA)
Automatically adjusts CPU and memory requests/limits for containers to rightsize workloads and eliminate over-provisioning.

### 3. Node Autoscaling
- **Cluster Autoscaler**: Monitors for unschedulable Pods (due to insufficient node capacity) and triggers cloud provider VM scaling.
- **Karpenter**: Open-source, high-performance node auto-provisioner that launches right-sized EC2 instances directly without node groups.""",
        key_concepts=[
            "HPA metric evaluation loops and stabilization windows",
            "KEDA (Kubernetes Event-driven Autoscaling) for message queues",
            "VPA recommendation modes (Off, Initial, Recreate, Auto)",
            "Karpenter just-in-time node provisioning and bin-packing"
        ],
        practical_example="""```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-autoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: enterprise-api
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 20
        periodSeconds: 60
```""",
        completion_req="Configure an HPA resource and simulate load scaling."
    ),
    make_lesson(
        title="Observability and Monitoring with Prometheus",
        slug="observability-and-monitoring-with-prometheus",
        order_index=10,
        duration_minutes=70,
        description="The three pillars of cloud-native observability: Metrics (Prometheus/Grafana), Logs (Fluentbit/Loki), and Traces (OpenTelemetry/Jaeger).",
        objectives=[
            "Deploy Prometheus and Grafana using the Prometheus Operator",
            "Instrument applications with Prometheus metrics (Counter, Gauge, Histogram, Summary)",
            "Formulate PromQL alerting rules and Golden Signals dashboards"
        ],
        content_body="""Cloud-native observability requires deep visibility into distributed systems across three core pillars: **Metrics**, **Logs**, and **Traces**.

### The Four Golden Signals (Google SRE)
1. **Latency**: Time it takes to service a request (differentiating successful requests from errors).
2. **Traffic**: Demand placed on the system (requests per second).
3. **Errors**: Rate of requests that fail explicitly or implicitly.
4. **Saturation**: Utilization percentage of the most constrained resource (CPU, memory, disk I/O, connection pools).

### Prometheus Operator & ServiceMonitors
The Prometheus Operator introduces Custom Resource Definitions (CRDs):
- `Prometheus`: Defines a Prometheus deployment.
- `ServiceMonitor`: Declaratively specifies how groups of Services should be monitored and scraped.
- `PrometheusRule`: Defines recording rules and alert conditions evaluated against PromQL queries.""",
        key_concepts=[
            "The 3 pillars: Metrics, Logs, and Distributed Traces",
            "Prometheus pull model and time-series datastore",
            "Four Golden Signals and RED/USE monitoring methodologies",
            "PromQL queries, vector matching, and Alertmanager routing"
        ],
        practical_example="""```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: app-service-monitor
  labels:
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      app: enterprise-backend
  endpoints:
  - port: metrics
    path: /metrics
    interval: 15s
```""",
        completion_req="Set up a ServiceMonitor and execute PromQL metric queries."
    )
]

# 10 Questions for Module 1 Quiz
MODULE_1_QUIZ_QUESTIONS = [
    make_question(1, "Which of the following is NOT one of the five NIST essential characteristics of cloud computing?", "Fixed physical hardware allocation", ["Broad network access", "On-demand self-service", "Rapid elasticity"], "NIST defines on-demand self-service, broad network access, resource pooling, rapid elasticity, and measured service. Fixed physical hardware is antithetical to cloud computing."),
    make_question(2, "In the Cloud Shared Responsibility Model for IaaS, who is responsible for patching the guest operating system?", "The Customer", ["The Cloud Provider", "The Hardware Vendor", "The Internet Service Provider"], "In IaaS, the customer manages the guest operating system, runtime, applications, and data."),
    make_question(3, "Which cloud service model abstracts the operating system and runtime, allowing developers to deploy code directly?", "PaaS (Platform as a Service)", ["IaaS (Infrastructure as a Service)", "SaaS (Software as a Service)", "FaaS (Firmware as a Service)"], "PaaS provides the hardware, OS, and runtime environment so developers only manage application code and config."),
    make_question(4, "What is the primary purpose of the Circuit Breaker architectural pattern?", "Prevent cascading failures by failing fast when a downstream service is unhealthy", ["Encrypt network traffic between microservices", "Distribute database load evenly across all tables", "Cache static assets at edge locations"], "Circuit Breakers prevent an application from continually invoking a failing remote dependency, allowing it time to recover."),
    make_question(5, "In Domain-Driven Design (DDD) for microservices, what concept defines the boundary of a domain model?", "Bounded Context", ["API Gateway", "Data Lake", "Virtual Private Cloud"], "A Bounded Context defines the explicit boundary within which a particular domain model applies."),
    make_question(6, "Which Linux kernel feature provides process isolation for PID, network, and mount points?", "Namespaces", ["cgroups", "Seccomp", "UnionFS"], "Namespaces isolate system resources (PID, NET, MNT, IPC, UTS, USER) per container."),
    make_question(7, "Which Linux kernel feature is responsible for limiting and metering CPU and memory consumption of containers?", "cgroups (Control Groups)", ["Namespaces", "AppArmor", "iptables"], "Control Groups (cgroups) allocate, throttle, and monitor hardware resource usage."),
    make_question(8, "Why are multi-stage builds recommended in Dockerfiles?", "They create smaller production images by excluding build-time tools and compilers", ["They make container startup slower for security", "They allow running multiple operating systems simultaneously", "They automatically disable all networking"], "Multi-stage builds allow copying only the compiled artifacts and minimal runtime dependencies into the final image."),
    make_question(9, "Which storage type is ideal for high-durability, flat-namespace, HTTP REST-accessible unstructured data?", "Object Storage (e.g., S3 / GCS)", ["Block Storage (e.g., EBS)", "File Storage (e.g., NFS)", "Local Instance Store"], "Object Storage provides 11 9s durability and RESTful access for unstructured objects and media."),
    make_question(10, "What does the Recovery Point Objective (RPO) measure in disaster recovery planning?", "The maximum acceptable amount of data loss measured in time", ["The time required to restore operations after a disaster", "The financial cost of running a backup region", "The network latency between availability zones"], "RPO defines the maximum acceptable age of files/data that must be recovered from backup storage for normal operations to resume.")
]

# 10 Questions for Module 2 Quiz
MODULE_2_QUIZ_QUESTIONS = [
    make_question(1, "Which Kubernetes Control Plane component acts as the single entry point for all administrative and node API requests?", "kube-apiserver", ["kube-scheduler", "kube-controller-manager", "etcd"], "All cluster communication flows through the kube-apiserver REST interface."),
    make_question(2, "What distributed consensus algorithm does etcd use to maintain state consistency across replicas?", "Raft", ["Paxos", "Proof of Stake", "Two-Phase Commit"], "etcd uses the Raft consensus algorithm for distributed leader election and log replication."),
    make_question(3, "What is the smallest deployable computing unit in Kubernetes?", "Pod", ["Container", "ReplicaSet", "Service"], "A Pod is the smallest atomic execution unit in Kubernetes, wrapping one or more containers."),
    make_question(4, "Which container type in a Pod runs to completion before any application containers are started?", "Init Container", ["Sidecar Container", "Ephemeral Container", "Adapter Container"], "Init containers execute sequentially and must complete successfully before main containers start."),
    make_question(5, "What is the default Service type in Kubernetes that allocates an internal virtual cluster IP?", "ClusterIP", ["NodePort", "LoadBalancer", "ExternalName"], "ClusterIP is the default service type, providing an internal stable IP accessible only within the cluster."),
    make_question(6, "Which node component manages iptables/IPVS rules to route Service virtual IPs to backing Pod IPs?", "kube-proxy", ["kubelet", "containerd", "CoreDNS"], "kube-proxy reflects Kubernetes Services on each node and performs Layer 4 connection forwarding."),
    make_question(7, "What is the primary difference between a Kubernetes Service and an Ingress resource?", "Service operates at Layer 4 (TCP/UDP); Ingress operates at Layer 7 (HTTP/HTTPS)", ["Service only supports external traffic; Ingress only supports internal traffic", "Service cannot load balance; Ingress only load balances", "There is no difference"], "Services handle Layer 4 network routing while Ingress provides Layer 7 HTTP/HTTPS routing, host matching, and SSL termination."),
    make_question(8, "Which Kubernetes controller is purpose-built for stateful workloads requiring stable network IDs and dedicated storage?", "StatefulSet", ["Deployment", "DaemonSet", "Job"], "StatefulSets provide stable unique network hostnames, ordered rollouts, and persistent volume bindings."),
    make_question(9, "What is the primary function of Helm in Kubernetes environments?", "Package manager for templating, versioning, and deploying Kubernetes manifests", ["Operating system hypervisor for worker nodes", "Network firewall for container traffic", "Container image vulnerability scanner"], "Helm provides templating (Go templates), dependency management, and versioned releases for Kubernetes."),
    make_question(10, "Which autoscaling component in Kubernetes scales the number of Pod replicas based on metric utilization?", "Horizontal Pod Autoscaler (HPA)", ["Vertical Pod Autoscaler (VPA)", "Cluster Autoscaler", "Karpenter"], "HPA automatically adjusts the replica count of a Deployment or ReplicaSet based on CPU, memory, or custom metrics.")
]

# 20 Questions for Final Assessment Quiz
FINAL_QUIZ_QUESTIONS = [
    make_question(1, "What core principle differentiates cloud elasticity from traditional scalability?", "Elasticity dynamically adapts resource provisioning in real-time matching demand fluctuations", ["Scalability requires zero human configuration", "Elasticity only applies to on-premises bare metal", "Scalability means using multiple cloud providers"], "Elasticity is the instantaneous, automated scaling up and down of resources as workload demand shifts."),
    make_question(2, "In microservices architectures, which pattern solves data consistency across distributed databases without two-phase commit?", "Saga Pattern", ["Monolithic Locking Pattern", "Singleton Pattern", "Factory Pattern"], "The Saga pattern coordinates a series of local transactions with corresponding compensating transactions on failure."),
    make_question(3, "What happens when a container exceeds its memory limit configured in its cgroup definition?", "The Linux kernel OOM killer terminates the container process (OOMKilled)", ["The container CPU is throttled to 0%", "The container automatically scales up its limit", "Traffic is diverted to another port"], "When memory exceeds the cgroup `memory.limit_in_bytes`, the kernel terminates the offending process with an OOM (Out Of Memory) event."),
    make_question(4, "Which OCI specification defines how container images are unpacked and executed as operating system processes?", "OCI Runtime Specification (runc)", ["OCI Image Specification", "OCI Distribution Specification", "CSI Specification"], "The OCI Runtime Spec outlines configuration and lifecycle execution implemented by runc."),
    make_question(5, "In a Kubernetes cluster, where is the persistent cluster configuration and state stored?", "etcd", ["kube-apiserver memory", "Worker node local disk", "kube-scheduler cache"], "etcd is the authoritative, highly available distributed key-value store for all Kubernetes state."),
    make_question(6, "What is the role of the kubelet on a Kubernetes worker node?", "Agent that communicates with kube-apiserver and ensures containers described in PodSpecs are running", ["Schedules unassigned Pods to available nodes", "Provides DNS resolution for the cluster", "Maintains etcd quorum"], "kubelet runs on every worker node, registering the node and executing PodSpecs via the container runtime."),
    make_question(7, "What happens during a RollingUpdate deployment when `maxUnavailable` is set to 0 and `maxSurge` is set to 1?", "Kubernetes creates 1 new Pod before terminating any old Pods, ensuring 100% capacity at all times", ["All old Pods are immediately terminated", "No updates can occur", "Only 1 Pod runs in the entire cluster"], "With maxUnavailable=0 and maxSurge=1, Kubernetes adds new replicas before scaling down old replicas, maintaining full capacity."),
    make_question(8, "How does CoreDNS resolve an internal query for `user-service.default.svc.cluster.local`?", "It returns the virtual ClusterIP associated with the user-service in the default namespace", ["It routes traffic directly to the external internet", "It queries the public root DNS servers", "It returns the MAC address of the worker node"], "CoreDNS resolves in-cluster service names to their corresponding virtual ClusterIP addresses."),
    make_question(9, "What Kubernetes resource enables automated management, issuance, and renewal of TLS certificates via Let's Encrypt?", "cert-manager", ["kube-proxy", "Helm", "Karpenter"], "cert-manager is the standard Kubernetes certificate controller for automated X.509 certificate lifecycle."),
    make_question(10, "Why should sensitive credentials in Kubernetes Secrets be encrypted at rest in etcd?", "By default, Secrets in etcd are stored unencrypted in plain Base64 encoding", ["Base64 is a military-grade encryption cipher", "Kubernetes automatically deletes unencrypted secrets", "etcd cannot store strings longer than 16 bytes"], "Base64 is an encoding scheme, not encryption; enabling KMS encryption at rest protects etcd storage media from unauthorized access."),
    make_question(11, "Which storage access mode allows multiple Kubernetes nodes to mount the volume concurrently for reading and writing?", "ReadWriteMany (RWX)", ["ReadWriteOnce (RWO)", "ReadOnlyMany (ROX)", "ReadWriteOncePod (RWOP)"], "ReadWriteMany (RWX) allows simultaneous read-write access across multiple cluster nodes (e.g., NFS, CephFS)."),
    make_question(12, "In Helm 3, where is release state metadata stored by default?", "In Kubernetes Secrets within the release namespace", ["In a dedicated Tiller pod", "In an external SQLite database on the client machine", "In the Helm binary"], "Helm 3 eliminated Tiller and stores versioned release state directly in Kubernetes Secrets within the target namespace."),
    make_question(13, "What algorithm does Horizontal Pod Autoscaler use to calculate desired replica count?", "`desiredReplicas = ceil[currentReplicas * (currentMetricValue / targetMetricValue)]`", ["`desiredReplicas = currentReplicas + 10`", "`desiredReplicas = maxReplicas - minReplicas`", "`desiredReplicas = currentReplicas / targetMetricValue`"], "HPA computes the ratio between current and target metric values to dynamically adjust replicas."),
    make_question(14, "Which tool provides just-in-time, fast node auto-provisioning for Kubernetes on AWS without node groups?", "Karpenter", ["Kube-router", "Flannel", "CoreDNS"], "Karpenter evaluates unschedulable pod requirements and provisions optimal EC2 instances directly via AWS APIs."),
    make_question(15, "In Prometheus monitoring, what metric type is an accumulative value that can only increase or reset to zero on restart?", "Counter", ["Gauge", "Histogram", "Summary"], "A Counter is a cumulative metric representing a single monotonically increasing value (e.g., total HTTP requests served)."),
    make_question(16, "What is a PromQL instant vector?", "A set of time series containing a single sample for each time series, all sharing the same timestamp", ["A time series spanning a continuous historical duration", "A scalar floating point number", "A string log line"], "An instant vector represents the latest single sample value for each matching time series buffer."),
    make_question(17, "What is the primary role of a ServiceMesh (such as Istio or Linkerd) in a Kubernetes cluster?", "Provides uniform Layer 7 traffic management, mutual TLS (mTLS) encryption, and telemetry without changing code", ["Replaces the Linux kernel on worker nodes", "Manages physical power supplies in the datacenter", "Compiles Go code into container binaries"], "A Service Mesh injects sidecar proxies to deliver zero-trust mTLS, intelligent routing, and distributed tracing transparently."),
    make_question(18, "Which Kubernetes probe determines if a container is alive and should be restarted if it fails?", "Liveness Probe", ["Readiness Probe", "Startup Probe", "Migration Probe"], "Liveness probes detect application deadlocks; if the probe fails, kubelet terminates and restarts the container."),
    make_question(19, "Which Kubernetes probe determines if a container is ready to accept incoming network traffic from a Service?", "Readiness Probe", ["Liveness Probe", "Eviction Probe", "Drain Probe"], "Readiness probes check if an app is initialized and healthy; if failing, the Pod is removed from Service endpoints."),
    make_question(20, "What is GitOps in modern cloud-native Kubernetes operations?", "Using Git repositories as the single source of truth for declarative infrastructure and automated deployments", ["Writing shell scripts directly on production servers", "Storing container images inside git commits", "Running git servers inside worker nodes"], "GitOps leverages Git PR workflows and automated reconcilers (ArgoCD/Flux) to synchronize cluster state with Git repositories.")
]

COURSE_1_DATA = {
    "title": "Cloud Architecture & Kubernetes at Scale",
    "slug": "cloud-architecture-kubernetes-scale",
    "level": "ADVANCED",
    "short_description": "Master enterprise cloud architecture, containerization, microservices, and production Kubernetes deployment at scale.",
    "description": "Comprehensive enterprise course covering cloud-native design patterns, containerization fundamentals, microservices decomposition, and end-to-end Kubernetes cluster architecture, networking, storage, orchestration, autoscaling, and observability.",
    "modules": [
        {
            "title": "Cloud-Native Architecture",
            "slug": "cloud-native-architecture",
            "order_index": 1,
            "description": "Foundational cloud concepts, service models, distributed architecture patterns, containerization, and cloud persistence.",
            "lessons": MODULE_1_LESSONS,
            "quiz": {
                "title": "Module 1 Quiz: Cloud-Native Architecture",
                "description": "Assess your understanding of cloud computing models, architectural patterns, microservices, and containerization fundamentals.",
                "passing_score": 70,
                "questions": MODULE_1_QUIZ_QUESTIONS
            }
        },
        {
            "title": "Kubernetes & Distributed Deployment",
            "slug": "kubernetes-distributed-deployment",
            "order_index": 2,
            "description": "In-depth Kubernetes architecture, control plane internals, workload management, networking, storage, Helm, and observability.",
            "lessons": MODULE_2_LESSONS,
            "quiz": {
                "title": "Module 2 Quiz: Kubernetes & Distributed Deployment",
                "description": "Assess your knowledge of Kubernetes components, workloads, networking, storage, Helm charts, and cluster autoscaling.",
                "passing_score": 70,
                "questions": MODULE_2_QUIZ_QUESTIONS
            }
        }
    ],
    "final_quiz": {
        "title": "Final Assessment: Cloud Architecture & Kubernetes at Scale",
        "description": "Comprehensive 20-question certification assessment covering the entire Cloud Architecture and Kubernetes curriculum.",
        "passing_score": 80,
        "questions": FINAL_QUIZ_QUESTIONS
    }
}
