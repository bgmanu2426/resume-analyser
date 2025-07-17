# 🎯 Resume Job Match Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Latest-brightgreen.svg)
![Redis](https://img.shields.io/badge/Redis-Queue-red.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

*An AI-powered resume analysis system that evaluates job fit and provides targeted recommendations for career advancement.*

</div>

## 📋 Problem Statement

In today's competitive job market, having a well-crafted resume is crucial for landing interviews and securing desired positions. However, many job seekers struggle with:

- **Uncertainty about job fit** - Not knowing if their current skills match specific job requirements
- **Lack of targeted feedback** - Generic resume advice that doesn't address specific career goals
- **Skills gap identification** - Difficulty understanding what qualifications are missing for desired roles
- **Resume optimization** - Unclear on how to highlight relevant experience for different job types
- **Career progression planning** - Limited guidance on what skills to develop for advancement

## 💡 Our Solution

**Resume Job Match Analyzer** is an intelligent, AI-powered system that solves these problems by providing:

### 🎯 **Job Fit Assessment**
- **Role compatibility analysis**: Evaluates how well your current resume matches specific job requirements
- **Skills gap identification**: Identifies missing qualifications and experience areas
- **Competency scoring**: Provides percentage match for different job roles and industries

### � **Targeted Recommendations**
- **Skill development roadmap**: Suggests specific skills to acquire for better job fit
- **Experience enhancement**: Recommends ways to gain relevant experience
- **Resume optimization**: Provides actionable points to improve resume for target roles

### �🔍 **Comprehensive Analysis**
- **Multi-page processing**: Converts PDF resumes to images for detailed visual analysis
- **AI-powered evaluation**: Uses Google's Gemini 2.0 Flash model for intelligent content analysis
- **Career progression insights**: Identifies next steps for professional growth

### ⚡ **Efficient Processing**
- **Asynchronous processing**: Queue-based system ensures fast response times
- **Real-time status tracking**: Monitor your resume analysis progress
- **Scalable architecture**: Handles multiple resume submissions simultaneously

### 🎨 **User-Friendly Experience**
- **Simple upload interface**: Easy drag-and-drop resume submission
- **Job role targeting**: Specify which position you're applying for
- **Email delivery**: Get your analysis delivered directly to your inbox
- **Job fit scoring**: Get instant compatibility scores for different roles
- **Actionable insights**: Receive specific recommendations for career advancement
- **Skills roadmap**: Clear guidance on what to learn or improve next

## 🛠️ Tech Stack

### **Backend Framework**
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.12+** - Latest Python version for optimal performance

### **AI & Machine Learning**
- **Google Gemini 2.0 Flash** - Advanced multimodal AI for resume analysis and job fit assessment
- **OpenAI SDK** - Compatible interface for Gemini API integration
- **PDF2Image** - PDF to image conversion for comprehensive visual analysis

### **Database & Storage**
- **MongoDB** - NoSQL database for flexible document storage
- **PyMongo** - Python driver for MongoDB operations

### **Queue & Background Processing**
- **Redis Queue (RQ)** - Simple job queue for Python
- **Valkey** - Redis-compatible in-memory data store

### **Email Delivery**
- **Resend** - Email API for sending analysis reports to users

### **Infrastructure & Deployment**
- **Docker & Docker Compose** - Containerized deployment
- **uvicorn** - ASGI server for FastAPI applications
- **aiofiles** - Asynchronous file operations

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        U[👤 User] --> API[🌐 FastAPI Server<br/>Port 8000]
    end
    
    subgraph "Application Layer"
        API --> UE[📤 Upload Endpoint<br/>/upload]
        API --> SE[📊 Status Endpoint<br/>/{file_id}]
        API --> HE[❤️ Health Check<br/>/]
    end
    
    subgraph "Queue Layer"
        UE --> RQ[🔄 Redis Queue<br/>Job Management]
        RQ --> W[⚙️ Worker Process<br/>Background Processing]
    end
    
    subgraph "Processing Layer"
        W --> PDF[📄 PDF to Image<br/>Converter]
        PDF --> AI[🤖 Gemini 2.0 Flash<br/>AI Analysis]
        AI --> JF[🎯 Job Fit<br/>Assessment]
        AI --> SG[📋 Skills Gap<br/>Analysis]
        AI --> REC[💡 Career<br/>Recommendations]
    end
    
    subgraph "Storage Layer"
        API -.-> DB[(🗄️ MongoDB<br/>Document Store)]
        W --> DB
        DB --> FD[📁 File Metadata]
        DB --> JS[📊 Job Scores]
        DB --> AR[📝 Analysis Results]
    end
    
    subgraph "External Services"
        AI -.-> GM[🌟 Google AI<br/>Gemini API]
        RQ -.-> VK[💾 Valkey<br/>Redis Storage]
    end
    
    %% Styling
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef apiClass fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef queueClass fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef processClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef storageClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef externalClass fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    
    class U,API,UE,SE,HE userClass
    class RQ,W queueClass
    class PDF,AI,JF,SG,REC processClass
    class DB,FD,JS,AR storageClass
    class GM,VK externalClass
```

### Architecture Flow

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant Queue
    participant Worker
    participant AI
    participant MongoDB
    
    User->>FastAPI: Upload PDF Resume
    FastAPI->>MongoDB: Store file metadata
    FastAPI->>Queue: Add processing job
    FastAPI-->>User: Return file_id
    
    Queue->>Worker: Assign job
    Worker->>Worker: Convert PDF to images
    Worker->>AI: Send images for analysis
    AI-->>Worker: Return job fit analysis
    Worker->>MongoDB: Store results
    
    User->>FastAPI: Check status (file_id)
    FastAPI->>MongoDB: Query results
    MongoDB-->>FastAPI: Return analysis
    FastAPI-->>User: Job fit & recommendations
```

## 📁 Project Structure

```mermaid
graph TD
    A[py_test] --> B[app/]
    A --> C[docker-compose.prod.yaml]
    A --> D[Dockerfile]
    A --> E[pyproject.toml]
    A --> F[README.md]
    A --> G[requirements.txt]
    A --> H[run.sh]
    A --> I[worker.sh]
    A --> J[uv.lock]
    A --> K[.env]
    
    B --> L[main.py]
    B --> M[server.py]
    B --> N[db/]
    B --> O[queue/]
    B --> P[utils/]
    
    N --> Q[__init__.py]
    N --> R[client.py]
    N --> S[db.py]
    N --> T[collections/]
    
    T --> U[__init__.py]
    T --> V[files.py]
    
    O --> W[__init__.py]
    O --> X[q.py]
    O --> Y[workers.py]
    
    P --> Z[__init__.py]
    P --> AA[file.py]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style N fill:#e8f5e8
    style O fill:#fff3e0
    style P fill:#fce4ec
```

## 🚀 Local Development Setup

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd py_test
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
# Google AI API Key (Get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install Dependencies
The project uses `uv` for fast dependency management:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 4. Start Services
You can run the application in two ways:

#### Option A: Using the provided script (Recommended)
```bash
chmod +x run.sh
./run.sh
```

#### Option B: Manual setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Start MongoDB (if running locally)
# Start Redis (if running locally)

# Start the FastAPI application
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, start the worker
rq worker --with-scheduler --url redis://localhost:6379
```

### 5. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000

## 🐳 Docker Deployment

### Development Environment
```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Production Environment
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yaml up -d --build
```

### Services Overview
- **app**: FastAPI application (Port 8000)
- **worker**: Background job processor (Port 8001)
- **mongo**: MongoDB database
- **valkey**: Redis-compatible queue storage

## 📚 API Documentation

### Upload Resume
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file (resume)

Response:
{
  "status": "File uploaded successfully",
  "file_id": "507f1f77bcf86cd799439011"
}
```

### Check Status & Get Analysis Results
```http
GET /{file_id}

Response:
{
  "message": "File found",
  "id": "507f1f77bcf86cd799439011",
  "FileName": "resume.pdf",
  "status": "processed successfully",
  "result": "Job fit analysis, skills assessment, and improvement recommendations..."
}
```

### Health Check
```http
GET /

Response:
{
  "status": "Hello World!"
}
```

## 🔄 Processing Flow

1. **Upload**: User uploads PDF resume via API
2. **Queue**: Resume processing job added to Redis queue
3. **Convert**: PDF pages converted to PNG images for comprehensive analysis
4. **Analyze**: All resume pages sent to Gemini AI for job fit assessment
5. **Evaluate**: AI determines compatibility with job roles and identifies skill gaps
6. **Recommend**: Generate targeted suggestions for career improvement
7. **Store**: Analysis results and recommendations saved to MongoDB
8. **Retrieve**: User can fetch job fit scores and improvement roadmap via API

## 🧪 Testing

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio httpx

# Run tests
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


<div align="center">
  <p>Made with ❤️ for career advancement</p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>
