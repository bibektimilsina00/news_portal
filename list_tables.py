import importlib
import pkgutil

from sqlmodel import SQLModel

# Import all modules under your 'modules' folder so SQLModel metadata registers all tables
import app.modules  # adjust this to your project structure

# Dynamically import all model files
package = app.modules
for _, module_name, _ in pkgutil.walk_packages(
    package.__path__, package.__name__ + "."
):
    importlib.import_module(module_name)

# Print all table names
for table_name in SQLModel.metadata.tables:
    print(table_name)
