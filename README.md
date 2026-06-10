# 🔍 Drishti - AI-Powered Crime Investigation System

**Drishti** (Sanskrit for "Vision") is an AI-powered investigative platform designed for the Karnataka State Police to modernize crime investigation through intelligent data analysis, multilingual support, and predictive analytics.

## 🌟 Features

### Core Capabilities
- **🤖 AI-Powered Chat Interface**: Natural language queries in English and Kannada
- **📚 RAG Pipeline**: Retrieval-Augmented Generation for context-aware responses
- **🕸️ Network Analysis**: Visual crime-criminal relationship graphs
- **📊 Predictive Analytics**: Crime forecasting and hotspot identification
- **🔐 Role-Based Access Control**: Hierarchical permissions (Constable, Inspector, SP, Admin)
- **📄 Report Generation**: PDF export of investigation sessions
- **🎤 Voice Input**: Speech-to-text for hands-free operation
- **🌐 Multilingual Support**: English and Kannada translation
- **📝 Audit Logging**: Complete activity tracking for accountability

### Technology Stack

**Backend:**
- FastAPI (Python) - High-performance API framework
- PostgreSQL (Supabase) - Relational database
- ChromaDB - Vector database for RAG
- Mistral AI - Large Language Model
- Prophet - Time-series forecasting
- NetworkX - Graph analysis

**Frontend:**
- React 19 + TypeScript
- Vite - Build tool
- TailwindCSS - Styling
- D3.js - Network visualization
- Recharts - Analytics charts
- Axios - HTTP client

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (for containerized deployment)
- Mistral API Key
- Supabase Account (or local PostgreSQL)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/drishti.git
cd drishti
```

### 2. Environment Setup

Create `.env` files in both backend and frontend directories:

**Backend `.env`:**
```bash
# Copy from template
cp backend/.env.example backend/.env

# Edit with your credentials
MISTRAL_API_KEY=your_mistral_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET_KEY=your_secure_random_secret
DATABASE_URL=postgresql://user:password@localhost:5432/drishti
```

**Frontend `.env`:**
```bash
# Copy from template
cp frontend/.env.example frontend/.env

# Edit with backend URL
VITE_API_URL=http://localhost:8000
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 5. Docker Deployment (Recommended)

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Login   │  │Dashboard │  │ Network  │  │  Audit   │   │
│  │  Page    │  │   Page   │  │  Page    │  │  Page    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │             │             │             │         │
│         └─────────────┴─────────────┴─────────────┘         │
│                          │                                   │
│                    Axios API Client                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Middleware Layer                     │  │
│  │  • CORS  • Authentication  • Rate Limiting             │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────┴────────────────────────┐        │
│  │              API Routes                          │        │
│  │  /auth  /chat  /network  /predictions  /export  │        │
│  └────────────────────┬────────────────────────────┘        │
│                       │                                      │
│  ┌──────────┬─────────┴────────┬─────────────┬────────┐    │
│  │   RAG    │    Mistral AI    │  Prophet    │Session │    │
│  │ Pipeline │    Client        │  Forecasts  │Manager │    │
│  └──────────┴──────────────────┴─────────────┴────────┘    │
└────────┬──────────────┬──────────────┬────────────────┬────┘
         │              │              │                │
         ▼              ▼              ▼                ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐    ┌─────────┐
  │ChromaDB  │   │PostgreSQL│   │Mistral AI│    │Audit DB │
  │(Vectors) │   │(Supabase)│   │   API    │    │  Logs   │
  └──────────┘   └──────────┘   └──────────┘    └─────────┘
```

## 📚 API Documentation

### Authentication Endpoints

#### `POST /api/auth/login`
Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "admin@ksp.gov.in",
  "password": "Admin@123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### `POST /api/auth/register`
Register new user (Admin only).

#### `GET /api/auth/me`
Get current user profile.

#### `GET /api/auth/verify`
Verify token validity.

### Chat Endpoints

#### `POST /api/chat/`
Submit query to AI assistant.

**Request:**
```json
{
  "message": "Show me theft cases in Bengaluru",
  "session_id": "session-uuid",
  "language": "en"
}
```

**Response:**
```json
{
  "response": "Based on the data, there are 145 theft cases...",
  "sources": [...],
  "confidence": 0.95
}
```

### Network Endpoints

#### `POST /api/network/graph`
Generate crime-criminal network graph.

**Request:**
```json
{
  "crime_id": 123,
  "criminal_name": "John Doe"
}
```

### Predictions Endpoints

#### `GET /api/predictions/forecast`
Get crime forecasts using Prophet.

**Query Params:**
- `district`: District name (default: "Bengaluru")
- `days`: Forecast period (default: 30)

#### `GET /api/predictions/hotspots`
Identify crime hotspots.

**Query Params:**
- `crime_type`: Type of crime (default: "theft")

#### `GET /api/predictions/alerts`
Get predictive alerts.

### Export Endpoints

#### `POST /api/export/pdf`
Generate PDF report of investigation session.

**Request:**
```json
{
  "chat_history": [...],
  "user_id": 1,
  "role": "inspector"
}
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    assigned_district VARCHAR(100),
    assigned_station_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Crimes Table
```sql
CREATE TABLE crimes (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    crime_date DATE NOT NULL,
    district VARCHAR(100) NOT NULL,
    police_station_id INTEGER NOT NULL,
    crime_type VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',
    lat FLOAT,
    lng FLOAT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Criminals Table
```sql
CREATE TABLE criminals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    criminal_history_count INTEGER DEFAULT 0,
    is_repeat_offender BOOLEAN DEFAULT FALSE,
    first_offense_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    ip_address VARCHAR(45),
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 👥 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Constable** | View crimes, basic chat queries, limited district access |
| **Inspector** | All constable permissions + network analysis, predictions |
| **SP (Superintendent)** | All inspector permissions + cross-district access, reports |
| **Admin** | Full system access, user management, audit logs |

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth with expiry
- **Password Hashing**: Bcrypt for secure password storage
- **Role-Based Access Control**: Hierarchical permission system
- **Rate Limiting**: Prevent API abuse
- **Audit Logging**: Complete activity tracking
- **CORS Protection**: Configured origin restrictions
- **Input Validation**: Pydantic schemas for request validation

## 🧪 Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

```bash
# Run backend tests
cd backend
pytest tests/ -v --cov

# Run frontend tests
cd frontend
npm run test
```

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Production Checklist
- [ ] Set secure JWT_SECRET_KEY
- [ ] Configure production database
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure Nginx reverse proxy
- [ ] Enable backup strategies
- [ ] Set up monitoring and logging
- [ ] Configure environment variables
- [ ] Test disaster recovery procedures

## 📊 Performance Metrics

- **API Response Time**: < 200ms (avg)
- **RAG Retrieval**: < 500ms
- **Chat Response**: < 2s (including LLM)
- **Network Graph**: < 1s for 100 nodes
- **PDF Generation**: < 3s

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is developed for Karnataka State Police. All rights reserved.

## 📞 Support

For issues, questions, or support:
- Create an issue in the repository
- Contact: support@drishti-ksp.gov.in
- Documentation: https://docs.drishti-ksp.gov.in

## 🙏 Acknowledgments

- Karnataka State Police for project requirements
- Mistral AI for language model capabilities
- Supabase for database infrastructure
- Open-source community for foundational tools

---

**Built with ❤️ for Karnataka State Police**
