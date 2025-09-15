#!/usr/bin/env python3

import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

if __name__ == "__main__":
    # Generate OpenAPI spec
    openapi_content = app.openapi()
    
    # Write to file
    with open("openapi.json", "w") as f:
        json.dump(openapi_content, f, indent=2)
    
    print("OpenAPI spec generated: openapi.json")