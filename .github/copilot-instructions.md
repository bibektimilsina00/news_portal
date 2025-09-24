# Copilot Instructions for News Portal API

## Architecture Overview

This is a comprehensive **News Portal API** built with FastAPI using **modular clean architecture** and **domain-driven design**:

```
app/
├── modules/          # Feature modules (authentication, users, posts, news, etc.)
│   ├── {module}/
│   │   ├── crud/     # Database operations
│   │   ├── model/    # SQLModel database models
│   │   ├── routes/   # FastAPI route handlers
│   │   ├── schema/   # Pydantic schemas for validation
│   │   └── services/ # Business logic layer
│   └── shared/       # Shared utilities across modules
├── core/            # Configuration, database, security
├── db_init/         # Database initialization
└── main.py          # FastAPI app entry point
```

**Key Pattern**: Each feature is a self-contained module with its own CRUD, models, routes, schemas, and services.

## Available Modules

- **authentication/** - JWT-based auth with tokens
- **users/** - User management with profiles and verification
- **posts/** - Social media posts with likes and bookmarks
- **news/** - News articles with categories and sources
- **stories/** - Instagram-style stories with highlights
- **reels/** - Short-form video content
- **live_streams/** - Live streaming functionality
- **social/** - Follows, comments, and shares
- **messaging/** - Direct messaging and chat
- **notifications/** - Push notifications and preferences
- **search/** - Content search with trending
- **media/** - Image and video management
- **content_moderation/** - Reporting and moderation
- **analytics/** - Usage analytics and metrics
- **monetization/** - Payments and subscriptions
- **ai_features/** - AI-powered features
- **integrations/** - Third-party integrations

## Development Commands

Use `uv` package manager for all Python operations:

- **Run app**: `uv run uvicorn app.main:app --reload`
- **Tests**: `uv run ./scripts/test.sh` or `uv run pytest`
- **DB migrations**: `uv run alembic upgrade head`
- **Install deps**: `uv add <package>` or `uv add --group dev <package>`

## Essential Patterns

### 1. Modular Architecture Pattern

Each module follows the same structure:

```python
# app/modules/{module}/schema/{entity}.py
class {Entity}Base(SQLModel):
    name: str = Field(max_length=100)
    # ... base fields

class {Entity}({Entity}Base, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # ... additional fields

class {Entity}Public({Entity}Base):
    id: uuid.UUID
    created_at: datetime
```

### 2. Layered Service Architecture

**Route → Service → CRUD → Model** (never skip layers)

```python
# routes/{module}.py
@router.get("/")
def read_entities(session: SessionDep, current_user: CurrentUser):
    entities = entity_service.get_entities(session)
    return entities

# services/{module}_service.py
def get_entities(session: SessionDep):
    return crud.entity.get_multi(session=session)

# crud/crud_{entity}.py
def get_multi(session: SessionDep):
    return session.exec(select(Entity)).all()
```

### 3. Cross-Module Relationships

Use `TYPE_CHECKING` for relationships between modules:

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.modules.users.model.user import User

class Post(PostBase, table=True):
    author_id: uuid.UUID = Field(foreign_key="user.id")
    author: "User" = Relationship(back_populates="posts")
```

### 4. Module Registration

Register new modules in `app/main.py`:

```python
from app.modules.posts.routes import posts as posts_router
from app.modules.users.routes import users as users_router

app.include_router(posts_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
```

## Security & Authentication

- **JWT tokens** with `app.core.security`
- **Password hashing** with bcrypt in CRUD layer
- **Dependencies**: `CurrentUser`, `SessionDep`, `get_current_active_superuser`
- **Superuser creation** handled in `app.core.db.init_db()`

## Database Patterns

- **SQLModel** for both Pydantic schemas and SQLAlchemy tables
- **UUID primary keys** with `uuid.uuid4` default factory
- **Alembic migrations** in `app/alembic/`
- **Relationships** use `cascade_delete=True` for proper cleanup
- **Session dependency** injection via `SessionDep`

## Import Conventions

```python
# Module-specific imports (preferred)
from app.modules.users.model.user import User
from app.modules.users.schema.user import UserCreate, UserPublic
from app.modules.users.services import user_service
from app.modules.users.crud import crud_user

# Shared utilities
from app.shared.deps.deps import SessionDep, CurrentUser
from app.shared.schema.message import Message

# Avoid generic imports like:
from app.modules.users import *  # Don't do this
```

## Module Development Workflow

### 1. Creating a New Module

```bash
# Create module structure
mkdir -p app/modules/{new_module}/{crud,model,routes,schema,services}

# Create empty files
touch app/modules/{new_module}/__init__.py
touch app/modules/{new_module}/{crud,model,routes,schema,services}/__init__.py
# ... create specific files
```

### 2. Module Dependencies

- **Core dependencies**: `SessionDep`, `CurrentUser`, `get_current_active_superuser`
- **Shared schemas**: `Message`, `UserPublic` (for relationships)
- **Cross-module imports**: Use `TYPE_CHECKING` for model relationships

### 3. Database Relationships

```python
# In posts/model/post.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.modules.users.model.user import User

class Post(PostBase, table=True):
    author_id: uuid.UUID = Field(foreign_key="user.id")
    author: "User" = Relationship(back_populates="posts")
```

## Testing & Quality

- **Pytest** with coverage reporting
- **Type checking** with mypy
- **Linting** with ruff
- **Test utilities** in `app/tests/utils/`

## Critical Files

- `app/shared/crud/base.py` - Generic CRUD base class with type safety
- `app/shared/deps/deps.py` - Dependency injection setup
- `app/core/config.py` - Environment-based configuration
- `app/main.py` - FastAPI app initialization with CORS/middleware
- `app/modules/{module}/routes/__init__.py` - Module router registration

When adding new features, follow the established domain pattern: create corresponding files in the appropriate module's crud/, model/, routes/, schema/, and services/ directories.
