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
- **Type checking**: `uv run mypy app/`
- **Linting**: `uv run ruff check app/`
- **Formatting**: `uv run ruff format app/`
- **Security checks**: `uv run bandit -r app/`
- **Coverage**: `uv run pytest --cov=app --cov-report=html`

### Make Targets

Common make targets for development:

```bash
make install          # Install dependencies
make run              # Run development server
make test             # Run tests with coverage
make test-fast        # Run tests without coverage
make lint             # Run linting and formatting
make type-check       # Run mypy type checking
make security         # Run security checks
make clean            # Clean cache files
make db-upgrade       # Run database migrations
make db-reset         # Reset database (dangerous!)
make docs             # Generate documentation
make docker-build     # Build Docker image
make docker-run       # Run with Docker
```

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
def get_multi(session: SessionDep) -> List[Entity]:
    statement = select(Entity).offset(skip).limit(limit)
    return list(session.exec(statement))
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

## Clean Code Principles

### SOLID Principles

- **Single Responsibility**: Each class/function has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes are substitutable for their base types
- **Interface Segregation**: Clients shouldn't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### DRY (Don't Repeat Yourself)

```python
# ❌ Bad: Repeated validation logic
def create_post(session: Session, post_data: PostCreate, user_id: UUID):
    if not post_data.title or len(post_data.title.strip()) == 0:
        raise ValueError("Title is required")
    if not post_data.content or len(post_data.content.strip()) == 0:
        raise ValueError("Content is required")
    # ... more validation

def update_post(session: Session, post_id: UUID, post_data: PostUpdate):
    if post_data.title is not None and len(post_data.title.strip()) == 0:
        raise ValueError("Title cannot be empty")
    if post_data.content is not None and len(post_data.content.strip()) == 0:
        raise ValueError("Content cannot be empty")
    # ... repeated validation

# ✅ Good: Extract validation to reusable function
def validate_post_data(title: str | None, content: str | None, require_all: bool = True) -> None:
    """Validate post title and content."""
    if require_all or title is not None:
        if not title or len(title.strip()) == 0:
            raise ValueError("Title is required and cannot be empty")
    if require_all or content is not None:
        if not content or len(content.strip()) == 0:
            raise ValueError("Content is required and cannot be empty")

def create_post(session: Session, post_data: PostCreate, user_id: UUID):
    validate_post_data(post_data.title, post_data.content)
    # ... rest of function

def update_post(session: Session, post_id: UUID, post_data: PostUpdate):
    validate_post_data(post_data.title, post_data.content, require_all=False)
    # ... rest of function
```

### Naming Conventions

```python
# ✅ Good: Descriptive names
class UserProfileManager:
    def update_user_profile(self, user_id: UUID, profile_data: dict) -> UserProfile:
        pass

def calculate_content_engagement_score(post: Post) -> float:
    pass

# ❌ Bad: Unclear abbreviations
class UPM:  # What is UPM?
    def upd_prof(self, uid: UUID, data: dict) -> UserProfile:  # unclear
        pass

def calc_score(p: Post) -> float:  # unclear what score
    pass
```

### Error Handling

```python
# ✅ Good: Specific exceptions with context
class UserNotFoundError(ValueError):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")

def get_user_or_fail(session: Session, user_id: UUID) -> User:
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user

# ✅ Good: Use Result types for complex operations
from typing import Result, Ok, Err

def process_payment(amount: Decimal, user_id: UUID) -> Result[Payment, str]:
    if amount <= 0:
        return Err("Amount must be positive")
    if not user_has_balance(user_id, amount):
        return Err("Insufficient balance")
    # ... process payment
    return Ok(payment)
```

### Function Design

```python
# ✅ Good: Small, focused functions
def can_user_post_content(user: User, content_type: str) -> bool:
    """Check if user can post content of given type."""
    if not user.is_active:
        return False
    if content_type == "news" and not user.is_journalist:
        return False
    return True

def validate_content_before_posting(content: str, user: User) -> None:
    """Validate content before posting."""
    if len(content.strip()) < 10:
        raise ValueError("Content too short")
    if not can_user_post_content(user, "post"):
        raise PermissionError("User cannot post content")

# ❌ Bad: Large function doing multiple things
def post_content(content: str, user_id: UUID, session: Session):
    # Get user
    user = session.get(User, user_id)
    if not user:
        raise ValueError("User not found")

    # Validate user permissions
    if not user.is_active:
        raise ValueError("User not active")
    if len(content) < 10:
        raise ValueError("Content too short")

    # Create post
    post = Post(content=content, author_id=user_id)
    session.add(post)
    session.commit()

    # Send notifications
    send_notifications(post)

    # Update analytics
    update_analytics(user_id, "post_created")
```

### Database Query Optimization

```python
# ✅ Good: Use selectinload for relationships
def get_posts_with_authors(session: Session, limit: int = 20) -> List[Post]:
    return list(session.exec(
        select(Post)
        .options(selectinload(Post.author))  # Load author with post
        .order_by(Post.created_at.desc())
        .limit(limit)
    ))

# ✅ Good: Use exists for existence checks
def user_has_liked_post(session: Session, user_id: UUID, post_id: UUID) -> bool:
    return session.exec(
        select(exists(
            select(Like)
            .where(Like.user_id == user_id, Like.post_id == post_id)
        ))
    ).one()

# ❌ Bad: Loading full objects for existence checks
def user_has_liked_post_bad(session: Session, user_id: UUID, post_id: UUID) -> bool:
    like = session.exec(
        select(Like)
        .where(Like.user_id == user_id, Like.post_id == post_id)
    ).first()
    return like is not None  # Loads unnecessary data
```

## Testing & Quality

### Testing Best Practices

- **Pytest** with coverage reporting (minimum 80% coverage)
- **Test utilities** in `app/tests/utils/`
- **Test structure**: `tests/{module}/test_{feature}.py`
- **Mock external dependencies** (APIs, databases for unit tests)
- **Use fixtures** for common test data
- **Test naming**: `test_{functionality}_{scenario}`

```python
# tests/conftest.py
@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password")
    )
    db_session.add(user)
    db_session.commit()
    return user

# tests/modules/users/test_user_service.py
def test_create_user_success(db_session: Session):
    """Test successful user creation."""
    user_data = UserCreate(
        email="new@example.com",
        username="newuser",
        password="password123"
    )
    user = UserService.create_user(
        session=db_session,
        user_create=user_data
    )
    assert user.email == user_data.email
    assert user.username == user_data.username
```

### Code Quality Tools

- **MyPy**: Strict type checking with comprehensive configuration
- **Ruff**: Fast Python linter and formatter
- **Bandit**: Security vulnerability scanner
- **Pre-commit hooks**: Automated quality checks

### MyPy Configuration Best Practices

```ini
# mypy.ini or pyproject.toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "tests.*",
    "scripts.*",
    "alembic.*"
]
ignore_errors = true
```

### Type Hints Best Practices

```python
# ✅ Good: Explicit types
def get_user_by_id(session: Session, user_id: UUID) -> User | None:
    return session.get(User, user_id)

# ✅ Good: Generic types
from typing import TypeVar
ModelType = TypeVar("ModelType", bound=SQLModel)

def get_or_404(session: Session, model: type[ModelType], id: UUID) -> ModelType:
    obj = session.get(model, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

# ❌ Bad: Any types
def process_data(data: Any) -> Any:
    return data

# ✅ Good: Union types
def validate_input(value: str | int | None) -> bool:
    return value is not None and len(str(value)) > 0
```

### SQLAlchemy Type Issues

Common mypy issues with SQLAlchemy/SQLModel and their fixes:

```python
# Column methods need type: ignore
.order_by(User.created_at.desc())  # type: ignore
.where(User.email.ilike(search_term))  # type: ignore
.where(User.id.in_(user_ids))  # type: ignore

# Session.exec returns Sequence, not List
return list(session.exec(select(User)))  # ✅ Correct
return session.exec(select(User)).all()  # ❌ Wrong

# Cast when mypy can't infer types
return cast(Optional[User], session.exec(select(User)).first())
```

## Development Workflow

### Git Best Practices

```bash
# Feature branch workflow
git checkout -b feature/add-user-profiles
# Make changes...
git commit -m "feat: add user profile management"
git push origin feature/add-user-profiles

# Commit message conventions
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code restructuring
test: add tests
chore: maintenance tasks
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Code Review Checklist

- [ ] **Type Safety**: All functions have proper type hints
- [ ] **Tests**: New features have corresponding tests (min 80% coverage)
- [ ] **Documentation**: Public APIs are documented
- [ ] **Security**: Input validation and authentication checks
- [ ] **Performance**: No N+1 queries, efficient database operations
- [ ] **Error Handling**: Proper exception handling and user-friendly messages
- [ ] **Clean Code**: Follows SOLID principles and DRY
- [ ] **Database**: Proper migrations for schema changes

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv sync
      - run: uv run make type-check
      - run: uv run make lint
      - run: uv run make test
      - run: uv run make security
```

### Performance Monitoring

```python
# Performance decorators
import time
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar('F', bound=Callable)

def measure_performance(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        # Log slow queries (>100ms)
        if duration > 0.1:
            logger.warning(f"Slow operation: {func.__name__} took {duration:.2f}s")

        return result
    return wrapper

# Usage
@measure_performance
def get_user_posts(session: Session, user_id: UUID) -> List[Post]:
    return list(session.exec(
        select(Post).where(Post.author_id == user_id)
    ))
```

## Critical Files

- `app/shared/crud/base.py` - Generic CRUD base class with type safety
- `app/shared/deps/deps.py` - Dependency injection setup
- `app/core/config.py` - Environment-based configuration
- `app/main.py` - FastAPI app initialization with CORS/middleware
- `app/modules/{module}/routes/__init__.py` - Module router registration

When adding new features, follow the established domain pattern: create corresponding files in the appropriate module's crud/, model/, routes/, schema/, and services/ directories.
