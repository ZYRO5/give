# Setup Instructions

## Initial Setup

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env with your configuration
nano .env

# Initialize database
python -m app.database.init

# Run development server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run development server
npm run dev
```

### 3. Database Setup

```bash
# Using Docker
docker run --name donor_db \
  -e POSTGRES_USER=donor_user \
  -e POSTGRES_PASSWORD=donor_password \
  -e POSTGRES_DB=donor_db \
  -p 5432:5432 \
  -d postgres:15-alpine

# Or using PostgreSQL locally
createdb donor_db
```

### 4. Redis Setup

```bash
# Using Docker
docker run --name donor_redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Or using Redis locally
redis-server
```

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# With coverage
pytest tests/ --cov=app

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
pylint app/
flake8 app/

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "migration message"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Production Deployment

### Using Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/donor_db

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-very-secret-key-here
ALGORITHM=HS256

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Admin
ADMIN_EMAIL=admin@donorplatform.com
ADMIN_PASSWORD=secure-password
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env
   - Run: `psql -h localhost -U donor_user -d donor_db`

2. **Redis Connection Error**
   - Ensure Redis is running
   - Check REDIS_URL in .env
   - Run: `redis-cli ping`

3. **Port Already in Use**
   - Backend: `sudo lsof -i :8000`
   - Frontend: `sudo lsof -i :3000`
   - Kill process: `kill -9 <PID>`

4. **Module Not Found Errors**
   - Ensure virtual environment is activated
   - Run: `pip install -r requirements.txt`

## Support

For issues and questions:
- Open an issue on GitHub
- Email: support@donorplatform.com
