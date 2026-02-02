# LAP - Quick Start Guide

## 🚀 Quick Start with Docker (Recommended)

### 1. Prerequisites
- Docker and Docker Compose installed
- Git

### 2. Clone and Start

```bash
# Clone the repository
git clone https://github.com/dans91364-create/lap.git
cd lap

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d
```

### 3. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@lap.com / admin)

### 4. Initialize Data

```bash
# Access the app container
docker-compose exec app bash

# Initialize database
python manage.py init

# Load municipalities
python manage.py load-municipios

# Start collecting data for a specific municipality
python manage.py collect -m 5208707 -y 2
```

## 💻 Local Development Setup

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local database settings
```

### 3. Start Services

```bash
# Start PostgreSQL and Redis (if not already running)
# Or use Docker for just the databases:
docker-compose up -d postgres redis

# Initialize database
python manage.py init

# Load municipalities
python manage.py load-municipios
```

### 4. Run the API

```bash
# Start the API server
python manage.py run-api

# Or use uvicorn directly
uvicorn src.api.main:app --reload
```

### 5. Run the Scheduler (Optional)

The scheduler will automatically run when you start the API if `SCHEDULER_ENABLED=true` in your .env file.

To run collection manually:

```bash
# Collect for all municipalities
python manage.py collect -y 2

# Collect for specific municipality
python manage.py collect -m 5208707 -y 2

# Check system status
python manage.py status
```

## 📊 Using the API

### Example API Calls

```bash
# List municipalities
curl http://localhost:8000/api/v1/municipios/

# Get specific municipality
curl http://localhost:8000/api/v1/municipios/5208707

# List biddings
curl http://localhost:8000/api/v1/licitacoes/?skip=0&limit=10

# Search biddings
curl -X POST http://localhost:8000/api/v1/licitacoes/search \
  -H "Content-Type: application/json" \
  -d '{"palavra_chave": "pavimentação", "limit": 10}'

# Get count
curl http://localhost:8000/api/v1/licitacoes/stats/count
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_collectors.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### API Not Starting

```bash
# Check logs
docker-compose logs app

# Rebuild the container
docker-compose up -d --build app
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Next Steps

1. Read the full [README.md](../README.md)
2. Check [API Documentation](API.md)
3. Review [Contributing Guidelines](../CONTRIBUTING.md)
4. Explore the interactive API docs at http://localhost:8000/docs

## 🆘 Need Help?

Open an issue on GitHub: https://github.com/dans91364-create/lap/issues
