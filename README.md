# 🚀 News Portal API

A comprehensive **News Portal API** built with FastAPI, featuring modular clean architecture, domain-driven design, and a complete social media platform with news, posts, stories, reels, live streaming, and more.

## 🛠 What's Inside the Box?

This is a full-featured news and social media platform API with everything you need:

- **FastAPI**: Modern, high-performance web framework with automatic OpenAPI documentation
- **PostgreSQL**: Robust relational database with SQLAlchemy/SQLModel ORM
- **UV Package Manager**: Lightning-fast Python package management
- **Docker**: Containerized deployment with blue-green deployment strategy
- **Alembic**: Database migration management
- **JWT Authentication**: Secure token-based authentication system
- **Modular Architecture**: Clean separation of concerns with feature-based modules
- **Real-time Features**: Live streaming, stories, notifications, and messaging
- **Media Management**: Image and video processing with cloud storage support
- **AI Features**: AI-powered content analysis and recommendations
- **Monetization**: Payment processing and subscription management

## 📦 Available Modules

The API is organized into self-contained modules:

- **Authentication** - JWT-based auth with OAuth2 support
- **Users** - User management with profiles and verification
- **Posts** - Social media posts with likes and bookmarks
- **News** - News articles with categories and sources
- **Stories** - Instagram-style stories with highlights
- **Reels** - Short-form video content
- **Live Streams** - Live streaming functionality with viewers
- **Media** - Image and video management with processing
- **Messaging** - Direct messaging and chat system
- **Notifications** - Push notifications and preferences
- **Search** - Content search with trending algorithms
- **Content Moderation** - Reporting and moderation tools
- **Analytics** - Usage analytics and metrics
- **Monetization** - Payments and subscriptions
- **AI Features** - AI-powered content features
- **Integrations** - Third-party service integrations

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) - For containerized development
- [UV](https://github.com/astral-sh/uv) - Modern Python package manager
- [Git](https://git-scm.com/) - Version control

### Local Development Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/bibektimilsina00/news-portal.git
   cd news-portal
   ```

2. **Setup Environment**

   Copy the example environment file and configure your settings:

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secrets
   ```

3. **Install Dependencies**

   ```bash
   uv sync
   ```

4. **Start Database**

   ```bash
   docker run -d \
     --name postgres \
     -p 5432:5432 \
     -e POSTGRES_USER=news_portal \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=news_portal_dev \
     postgres:16-alpine
   ```

5. **Run Migrations**

   ```bash
   uv run alembic upgrade head
   ```

6. **Start Development Server**

   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at http://localhost:8000 with automatic documentation at http://localhost:8000/docs

### Docker Development

For a complete containerized development environment:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use the build script
./build.sh --env development --version dev
```

## 🗄 Database Operations

### Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "Add new feature"

# Apply migrations
uv run alembic upgrade head

# Downgrade
uv run alembic downgrade -1
```

### Database Reset (Development)

```bash
# Reset database (dangerous!)
uv run alembic downgrade base
uv run alembic upgrade head
```

## 🧪 Testing & Quality

### Run Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html

# Specific test file
uv run pytest tests/modules/users/test_user_service.py
```

### Code Quality

```bash
# Type checking
uv run mypy app/

# Linting and formatting
uv run ruff check app/
uv run ruff format app/

# Security checks
uv run bandit -r app/
```

### Development Commands

```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name
uv add --group dev package-name

# Run development server
uv run uvicorn app.main:app --reload

# Run with hot reload
make run

# Run all quality checks
make lint

# Run tests
make test
```

## 🚀 Deployment

### Production Build

```bash
# Build production image
./build.sh --env production --version 1.0.0 --push

# Deploy to server
./deploy.sh main
```

### Blue-Green Deployment

The deployment script supports zero-downtime blue-green deployment:

```bash
# Deploy main branch
./deploy.sh main

# Deploy develop branch
./deploy.sh develop

# Force clean deployment
./deploy.sh main force
```

### Environment Configuration

Create appropriate `.env` files for each environment:

- `.env` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## � Configuration

Key environment variables:

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=news_portal
POSTGRES_PASSWORD=password
POSTGRES_DB=news_portal_prod

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Media Storage (optional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET_NAME=your-bucket
```

## 🏗 Architecture

### Modular Structure

```
app/
├── modules/          # Feature modules
│   ├── {module}/
│   │   ├── crud/     # Database operations
│   │   ├── model/    # SQLModel database models
│   │   ├── routes/   # FastAPI route handlers
│   │   ├── schema/   # Pydantic schemas
│   │   └── services/ # Business logic
│   └── shared/       # Shared utilities
├── core/            # Configuration, database, security
├── db_init/         # Database initialization
└── main.py          # FastAPI app entry point
```

### Key Patterns

- **Layered Architecture**: Route → Service → CRUD → Model
- **Dependency Injection**: SessionDep, CurrentUser dependencies
- **Type Safety**: Full mypy type checking
- **Clean Code**: SOLID principles and DRY
- **Domain-Driven Design**: Feature-based module organization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper tests
4. Run quality checks: `make lint && make test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Follow the established module structure
- Add tests for new features
- Update documentation as needed
- Ensure type safety with mypy
- Follow the commit message conventions

## 📜 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database ORM with [SQLModel](https://sqlmodel.tiangolo.com/)
- Package management with [UV](https://github.com/astral-sh/uv)
- Inspired by full-stack-fastapi-postgresql template

---

**Ready to build the next generation news platform? 🚀**
