# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose (optional)
- PostgreSQL (for production) or SQLite (for development)

## Setup

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp env.example .env
```

5. Update `.env` with your configuration

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the server:
```bash
uvicorn app.main:app --reload
```

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment file:
```bash
cp env.example .env.local
```

4. Update `.env.local` with your configuration

5. Start development server:
```bash
npm run dev
```

## Running Tests

### Backend

```bash
cd backend
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm test
```

## Code Style

### Python

- Use Black for formatting
- Use flake8 for linting
- Follow PEP 8

### TypeScript/JavaScript

- Use ESLint
- Follow Next.js conventions

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   ├── utils/        # Utility functions
│   └── exceptions/   # Custom exceptions
├── database/         # Database models
├── migrations/       # Alembic migrations
└── tests/            # Tests

frontend/
├── app/              # Next.js app directory
├── components/       # React components
└── lib/              # Utility libraries
```

