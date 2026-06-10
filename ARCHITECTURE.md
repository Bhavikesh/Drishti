# 🏛️ System Architecture Documentation

## Overview

Drishti is a modern, microservices-inspired architecture that combines AI/ML capabilities with traditional web application patterns. The system is designed for scalability, maintainability, and security.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Web App    │  │  Mobile Web  │  │  Desktop     │             │
│  │   (React)    │  │  (Responsive)│  │  (Electron)  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API Gateway / Load Balancer                     │
│                         (Nginx / AWS ALB)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Layer (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    Middleware Stack                         │    │
│  │  • CORS Handler                                             │    │
│  │  • Authentication Middleware (JWT)                          │    │
│  │  • Rate Limiting                                            │    │
│  │  • Request Logging                                          │    │
│  └────────────────────────────────────────────────────────────┘    │
│                               │                                      │
│  ┌────────────────────────────┴────────────────────────────┐       │
│  │                     API Routes                           │       │
│  │  /auth • /chat • /network • /predictions • /export      │       │
│  └────────────────────────┬─────────────────────────────────┘       │
│                           │                                          │
│  ┌────────────────────────┴─────────────────────────────────┐      │
│  │                   Business Logic Layer                     │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │      │
│  │  │   RAG    │  │ Mistral  │  │ Prophet  │  │ Network  │ │      │
│  │  │ Pipeline │  │  Client  │  │ Forecasts│  │ Analysis │ │      │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │      │
│  │  │  Trans-  │  │ Session  │  │  Audit   │  │   PDF    │ │      │
│  │  │ lation   │  │ Manager  │  │  Logger  │  │ Generator│ │      │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │      │
│  └──────────────────────────────────────────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐
│   PostgreSQL     │  │  ChromaDB    │  │   Mistral AI    │
│   (Supabase)     │  │  (Vector DB) │  │   API (Cloud)   │
│                  │  │              │  │                 │
│ • Users          │  │ • Crime      │  │ • LLM Queries   │
│ • Crimes         │  │   Embeddings │  │ • Chat          │
│ • Criminals      │  │ • Documents  │  │ • Completion    │
│ • Audit Logs     │  │ • Metadata   │  │                 │
└──────────────────┘  └──────────────┘  └─────────────────┘
```

## Component Architecture

### 1. Frontend Layer (React + TypeScript)

**Technology Stack:**
- React 19 (UI Framework)
- TypeScript (Type Safety)
- Vite (Build Tool)
- TailwindCSS (Styling)
- D3.js (Network Visualization)
- Recharts (Charts & Graphs)

**Structure:**
```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Chat.tsx
│   │   ├── NetworkGraph.tsx
│   │   └── PDFExport.tsx
│   ├── pages/           # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── NetworkPage.tsx
│   │   └── AuditPage.tsx
│   ├── contexts/        # React Context for state
│   │   └── AuthContext.tsx
│   ├── hooks/           # Custom React hooks
│   │   ├── useAuth.ts
│   │   └── useVoice.ts
│   ├── services/        # API service layer
│   │   ├── api.ts
│   │   └── voice.ts
│   └── types/           # TypeScript definitions
│       └── index.ts
```

**Key Features:**
- Single Page Application (SPA)
- Client-side routing
- JWT token management
- Real-time chat interface
- Interactive network graphs
- Voice input support

### 2. Backend Layer (FastAPI + Python)

**Technology Stack:**
- FastAPI (API Framework)
- Uvicorn (ASGI Server)
- Pydantic (Data Validation)
- SQLAlchemy (ORM, future)
- psycopg2 (PostgreSQL Driver)

**Structure:**
```
backend/
├── routes/              # API endpoints
│   ├── auth.py
│   ├── chat.py
│   ├── network.py
│   ├── predictions.py
│   └── export.py
├── schemas/             # Pydantic models
│   ├── user_schema.py
│   └── crime_schema.py
├── middlewares/         # Custom middleware
│   ├── auth_middleware.py
│   └── rate_limiter.py
├── utils/              # Utility modules
│   ├── audit_logger.py
│   └── session_manager.py
├── database.py         # Database connection
├── mistral_client.py   # Mistral AI integration
├── rag_pipeline.py     # RAG implementation
├── translation.py      # Translation services
└── main.py            # Application entry point
```

### 3. Data Layer

#### 3.1 PostgreSQL (Relational Database)

**Schema Design:**

```sql
-- Users Table
users
├── id (PK)
├── email
├── password_hash
├── role
├── assigned_district
├── assigned_station_id
└── created_at

-- Crimes Table
crimes
├── id (PK)
├── case_id (UNIQUE)
├── crime_date
├── district
├── police_station_id
├── crime_type
├── description
├── status
├── lat, lng
├── is_resolved
└── resolution_date

-- Criminals Table
criminals
├── id (PK)
├── name
├── age
├── gender
├── criminal_history_count
├── is_repeat_offender
└── first_offense_date

-- Crime-Criminal Association
crime_criminals
├── id (PK)
├── crime_id (FK)
├── criminal_id (FK)
└── role

-- Audit Logs
audit_logs
├── id (PK)
├── user_id (FK)
├── action
├── query
├── response
├── ip_address
├── session_id
└── timestamp
```

**Indexes:**
- `idx_crimes_district` on crimes(district)
- `idx_crimes_date` on crimes(crime_date)
- `idx_crimes_type` on crimes(crime_type)
- `idx_audit_user` on audit_logs(user_id)
- `idx_audit_timestamp` on audit_logs(timestamp)

#### 3.2 ChromaDB (Vector Database)

**Purpose:** Store and retrieve crime document embeddings for RAG

**Collections:**
- `drishti_crimes`: Crime case documents and metadata

**Features:**
- Semantic search
- Similarity matching
- Metadata filtering

### 4. AI/ML Services

#### 4.1 RAG Pipeline

**Components:**
1. **Document Loader**: Load crime records
2. **Text Splitter**: Chunk documents
3. **Embedding Model**: sentence-transformers
4. **Vector Store**: ChromaDB
5. **Retriever**: Semantic search
6. **LLM**: Mistral AI

**Flow:**
```
User Query
    ↓
Embedding
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve Top-K Documents
    ↓
Context + Query → Mistral AI
    ↓
Generated Response
```

#### 4.2 Mistral AI Integration

**Model:** Mistral Large or Mistral Medium
**Use Cases:**
- Natural language understanding
- Query answering
- Context-aware responses
- Multilingual support

#### 4.3 Prophet (Time Series Forecasting)

**Features:**
- Crime trend prediction
- Seasonal pattern detection
- Anomaly detection
- Confidence intervals

#### 4.4 NetworkX (Graph Analysis)

**Features:**
- Crime-criminal relationship graphs
- Community detection
- Centrality analysis
- Path finding

## Security Architecture

### Authentication Flow

```
1. User Login Request
    ↓
2. Validate Credentials (bcrypt)
    ↓
3. Generate JWT Token (HS256)
    ↓
4. Return Token to Client
    ↓
5. Client Stores Token (localStorage/memory)
    ↓
6. Subsequent Requests Include Token
    ↓
7. Auth Middleware Validates Token
    ↓
8. Extract User Info & Proceed
```

### Authorization Levels

| Role | Access Level |
|------|-------------|
| **Constable** | Read-only, assigned district only |
| **Inspector** | Read + Network Analysis, assigned district |
| **SP** | Read + Write + Predictions, cross-district |
| **Admin** | Full access + User management |

### Security Measures

1. **Password Security**
   - Bcrypt hashing (12 rounds)
   - Minimum complexity requirements
   - No plain text storage

2. **API Security**
   - JWT with expiration
   - Rate limiting (100 req/min)
   - CORS protection
   - Input validation (Pydantic)

3. **Data Security**
   - SQL injection prevention
   - XSS protection
   - HTTPS enforcement
   - Audit logging

4. **Network Security**
   - Firewall rules
   - Network isolation
   - VPC (in cloud deployments)

## Scalability Considerations

### Horizontal Scaling

**Backend:**
- Stateless design
- Load balancer distribution
- Multiple FastAPI instances

**Database:**
- Read replicas
- Connection pooling
- Query optimization

**ChromaDB:**
- Distributed deployment
- Sharding by district

### Caching Strategy

```
┌─────────────┐
│   Redis     │  ← Session cache
│   (Future)  │  ← Query results cache
└─────────────┘  ← Prediction cache
```

### Performance Optimization

1. **Database:**
   - Indexed columns
   - Query optimization
   - Connection pooling

2. **API:**
   - Async operations
   - Response compression
   - Pagination

3. **Frontend:**
   - Code splitting
   - Lazy loading
   - Asset optimization
   - CDN delivery

## Deployment Architecture

### Development Environment

```
Docker Compose
├── PostgreSQL Container
├── Backend Container
└── Frontend Container
```

### Production Environment (AWS Example)

```
┌─────────────────────────────────────────┐
│          AWS Cloud                       │
│  ┌────────────────────────────────┐    │
│  │   Route 53 (DNS)               │    │
│  └─────────────┬──────────────────┘    │
│                ↓                         │
│  ┌────────────────────────────────┐    │
│  │   CloudFront (CDN)             │    │
│  └─────────────┬──────────────────┘    │
│                ↓                         │
│  ┌────────────────────────────────┐    │
│  │   ALB (Load Balancer)          │    │
│  └─────────────┬──────────────────┘    │
│                ↓                         │
│  ┌────────────────────────────────┐    │
│  │   ECS/EKS (Containers)         │    │
│  │   ├── Backend (3 instances)    │    │
│  │   └── Frontend (2 instances)   │    │
│  └─────────────┬──────────────────┘    │
│                ↓                         │
│  ┌────────────────────────────────┐    │
│  │   RDS PostgreSQL (Multi-AZ)    │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │   S3 (Static Assets, Backups)  │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │   CloudWatch (Monitoring)      │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Monitoring & Observability

### Metrics to Track

1. **Application Metrics:**
   - Request rate
   - Response time
   - Error rate
   - Active users

2. **Infrastructure Metrics:**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network throughput

3. **Business Metrics:**
   - Queries per day
   - Response accuracy
   - User satisfaction
   - Feature usage

### Logging Strategy

**Log Levels:**
- ERROR: System failures
- WARN: Degraded performance
- INFO: Important events
- DEBUG: Detailed diagnostics

**Log Aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- CloudWatch Logs (AWS)
- Application logs
- Audit logs

## Disaster Recovery

### Backup Strategy

**Database Backups:**
- Full backup: Daily
- Incremental: Hourly
- Retention: 30 days
- Location: S3/Cloud Storage

**Vector Database:**
- Snapshot: Daily
- Retention: 7 days

**Recovery Time Objectives:**
- RTO: 4 hours
- RPO: 1 hour

### High Availability

**Components:**
- Multi-AZ database deployment
- Load balancer health checks
- Auto-scaling groups
- Automated failover

## Technology Decisions

### Why FastAPI?
- High performance (async)
- Automatic API documentation
- Python ecosystem integration
- Type safety with Pydantic

### Why React?
- Component reusability
- Rich ecosystem
- Strong TypeScript support
- Performance optimization

### Why PostgreSQL?
- ACID compliance
- Complex queries
- JSON support
- Proven reliability

### Why ChromaDB?
- Easy integration
- Built for embeddings
- Good performance
- Open source

### Why Mistral AI?
- Strong multilingual support
- Good price/performance
- EU-based (data sovereignty)
- API simplicity

## Future Enhancements

1. **Microservices Decomposition:**
   - Separate services for Chat, Network, Predictions
   - Event-driven architecture
   - Message queues (RabbitMQ/Kafka)

2. **Real-time Features:**
   - WebSocket support
   - Live dashboard updates
   - Push notifications

3. **Advanced AI:**
   - Custom model fine-tuning
   - Image analysis for evidence
   - Voice cloning detection
   - Sentiment analysis

4. **Mobile Application:**
   - React Native app
   - Offline support
   - GPS integration

5. **Advanced Analytics:**
   - PowerBI/Tableau integration
   - Custom report builder
   - Data export APIs

---

This architecture is designed to evolve with growing requirements while maintaining security, performance, and reliability.
