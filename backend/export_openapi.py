import sys
import os
import json

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.main import app

# Generate OpenAPI schema
schema = app.openapi()

# Write to frontend/openapi.json
output_path = os.path.join("..", "frontend", "openapi.json")
with open(output_path, "w") as f:
    json.dump(schema, f, indent=2)

print(f"OpenAPI schema exported to {output_path}")
