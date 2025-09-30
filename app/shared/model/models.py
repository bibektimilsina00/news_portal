# User Management
# AI Features Module

"""Central model registry.

This module programmatically imports all model modules under app.modules.*.model
so that SQLModel/SQLAlchemy mappers are registered before classes that use
string-based forward references (for example the User model) are imported.

This prevents InvalidRequestError: expression 'X' failed to locate a name ('X')
when initializing mappers during scripts like db_init.initial_data.
"""

from __future__ import annotations

import importlib
import os
import pkgutil
from pathlib import Path
from types import ModuleType

import app.modules as modules_pkg


def _import_all_model_modules(package: ModuleType) -> None:
    """Import every module under {package}.*.model.*"""
    base_path = package.__path__[0]
    for root, dirs, files in os.walk(base_path):
        # only consider files in a 'model' directory
        if os.path.basename(root) != "model":
            continue
        # derive module path from filesystem path
        rel_path = Path(root).relative_to(base_path)
        # parent package (e.g., app.modules.news.model)
        # rel_path.parts is like ('news','model') so use the first part
        if len(rel_path.parts) >= 1:
            module_name = rel_path.parts[0]
        else:
            # fallback
            module_name = Path(root).parts[-3]
        pkg_prefix = f"app.modules.{module_name}.model"
        for filename in files:
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            mod_name = filename[:-3]
            full_mod = f"{pkg_prefix}.{mod_name}"
            try:
                importlib.import_module(full_mod)
            except Exception as exc:
                failures.append((full_mod, exc))


# Import all model modules so relationships referencing classes by name
# (string forward refs) can be resolved when mappers are configured.
failures: list[tuple[str, Exception]] = []
_import_all_model_modules(modules_pkg)

if failures:
    # Print import failures to stderr to help debugging mapper registration
    import sys

    print("Model import failures:", file=sys.stderr)
    for mod, exc in failures:
        print(f" - {mod}: {exc!r}", file=sys.stderr)


# After loading all models, import user-related models for convenience
try:
    from app.modules.users.model.user import *  # noqa: F401,F403
    from app.modules.users.model.profile import *  # noqa: F401,F403
    from app.modules.users.model.verification import *  # noqa: F401,F403
except Exception:
    # If user models fail to import, let the caller handle the error; the
    # dynamic import above should have registered most required models
    # already.
    pass
# Notifications Module

# Posts Module

# Reels Module

# Reels Module

# Search Module

# Social Module

# Stories Module
from app.modules.stories.model.story import *
from app.modules.stories.model.viewer import *
from app.modules.stories.model.interaction import *
from app.modules.stories.model.highlight import *

# Users Module (profiles/verification rely on user model)
from app.modules.users.model.user import *
from app.modules.users.model.profile import *
from app.modules.users.model.verification import *
